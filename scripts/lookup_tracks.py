#!/usr/bin/env python3
"""Resolve JSON records or 'artist - title' text lines to Spotify tracks."""
import argparse
import json
import os
import re
from pathlib import Path
import sys
import time
import unicodedata
from difflib import SequenceMatcher

import requests


def log(message):
    print(message, file=sys.stderr, flush=True)


class Spotify:
    def __init__(self, client_id, client_secret, max_retry_wait=60):
        self.session = requests.Session()
        self.credentials = (client_id, client_secret)
        self.token = None
        self.expires = 0
        self.max_retry_wait = max_retry_wait

    def search(self, query):
        if time.monotonic() >= self.expires:
            log('Authenticating with Spotify… (request timeout: 30s)')
            response = self.session.post(
                'https://accounts.spotify.com/api/token', auth=self.credentials,
                data={'grant_type': 'client_credentials'}, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.token = data['access_token']
            self.expires = time.monotonic() + data['expires_in'] - 60
            log('Spotify authentication successful.')
        for attempt in range(4):
            time.sleep(0.5)
            log(f'  Search {attempt + 1}/4: {query}')
            response = self.session.get(
                'https://api.spotify.com/v1/search',
                headers={'Authorization': f'Bearer {self.token}'},
                params={'q': query, 'type': 'track', 'limit': 10}, timeout=30)
            if response.status_code == 429 and attempt < 3:
                delay = max(1, int(response.headers.get('Retry-After', '1')))
                if delay > self.max_retry_wait:
                    raise requests.RequestException(
                        f'Spotify rate limit: Retry-After is {delay}s. '
                        'Stop other lookup processes and wait at least that long before rerunning. '
                        f'No retry sent; automatic wait limit is {self.max_retry_wait}s. '
                        'Use --max-retry-wait SECONDS to allow a longer wait.')
                log(f'  Spotify rate limit: waiting the full {delay}s before retrying.')
                remaining = delay
                while remaining:
                    interval = min(remaining, 30)
                    time.sleep(interval)
                    remaining -= interval
                    if remaining:
                        log(f'  Rate-limit cooldown: {remaining}s remaining.')
                continue
            response.raise_for_status()
            tracks = response.json()['tracks']['items']
            log(f'  Received {len(tracks)} candidates.')
            return tracks


def read_tracks(path, station_num='', station_name='RADIOPORT'):
    content = path.read_text(encoding='utf-8-sig')
    if path.suffix.lower() == '.json' or content.lstrip().startswith('['):
        records = json.loads(content)
        if not isinstance(records, list):
            raise ValueError('JSON input must be an array.')
    else:
        records = []
        for number, line in enumerate(content.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            artist, separator, title = line.partition(' - ')
            if not separator:
                raise ValueError(f'Line {number}: expected artist - title')
            records.append({'artist': artist.strip(), 'track_title': title.strip()})
    result = []
    for number, record in enumerate(records, 1):
        if not isinstance(record, dict):
            raise ValueError(f'Record {number} must be an object.')
        title = record.get('track_title', record.get('title', ''))
        artist = record.get('artist', '')
        if not isinstance(title, str) or not title.strip() or not isinstance(artist, str) or not artist.strip():
            raise ValueError(f'Record {number} needs a title and artist.')
        result.append({**record, 'station_num': str(record.get('station_num', station_num)),
                       'station_name': str(record.get('station_name', station_name)),
                       'track_title': title.strip(), 'artist': artist.strip()})
    return result


def normalize(value):
    decomposed = unicodedata.normalize('NFKD', value.casefold())
    return re.sub(r'[^\w]+', ' ', ''.join(
        char for char in decomposed if not unicodedata.combining(char))).strip()


def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def artist_variants(record):
    names = []
    for field in ('artist', 'in_game_artist', 'performed_by'):
        credit = record.get(field)
        if not isinstance(credit, str) or not credit.strip():
            continue
        names.append(credit.strip())
        # Preserve source credits while also trying band names and performers
        # written inside parentheses, including featured collaborators.
        pieces = re.split(r'[()]', credit)
        for piece in pieces:
            piece = re.sub(r'^\s*(?:ft\.?|feat\.?)\s+', '', piece, flags=re.I)
            names.extend(re.split(r'\s+(?:and|ft\.?|feat\.?)\s+|[,;]\s*', piece, flags=re.I))
    return list(dict.fromkeys(name.strip() for name in names if name.strip()))


def resolve(record, spotify):
    title = record['track_title']
    artists = artist_variants(record)

    def scores(track):
        title_score = similarity(title, track['name'])
        artist_score = max((similarity(name, artist['name'])
                            for name in artists for artist in track['artists']), default=0)
        return title_score, artist_score

    def acceptable(track):
        title_score, artist_score = scores(track)
        return title_score >= 0.7 and artist_score >= 0.6

    candidates = {}
    # Retry aliases even when the first query returns unrelated, low-scoring songs.
    queries = [f'track:{title} artist:{artist}' for artist in artists]
    queries.append(f'{title} {record["artist"]}')
    for query in dict.fromkeys(queries):
        for track in spotify.search(query):
            candidates[track['uri']] = track
        valid = [track for track in candidates.values() if acceptable(track)]
        if any(sum(scores(track)) / 2 >= 0.85 for track in valid):
            break
    valid = [track for track in candidates.values() if acceptable(track)]
    best = max(valid or list(candidates.values()),
               key=lambda track: sum(scores(track)) / 2, default=None)
    output = {**record, 'uri': None, 'spotify_track_name': None,
              'album_artwork_url': None, 'match_status': 'not_found'}
    if best:
        confidence = sum(scores(best)) / 2
        output['match_score'] = round(confidence, 3)
        if acceptable(best) and confidence >= 0.65:
            images = best.get('album', {}).get('images', [])
            output.update(uri=best['uri'], spotify_track_name=best['name'],
                          spotify_artists=[artist['name'] for artist in best['artists']],
                          album_artwork_url=images[0]['url'] if images else None,
                          match_status='matched' if confidence >= 0.85 else 'review')
        else:
            output['match_status'] = 'low_confidence'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=Path('tracks.catalog.json'))
    parser.add_argument('--station-num', default='')
    parser.add_argument('--station-name', default='RADIOPORT')
    parser.add_argument('--refresh', action='store_true', help='Re-query tracks that already have a valid Spotify URI.')
    parser.add_argument('--max-retry-wait', type=int, default=60, help='Maximum automatic rate-limit wait in seconds (default: 60).')
    args = parser.parse_args()
    try:
        log(f'Reading {args.input}…')
        records = read_tracks(args.input, args.station_num, args.station_name)
        log(f'Loaded {len(records)} tracks. Output: {args.output}')
        client_id, secret = os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET')
        if not client_id or not secret:
            raise ValueError('Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.')
        if args.max_retry_wait < 0:
            raise ValueError('--max-retry-wait must be non-negative.')
        spotify = Spotify(client_id, secret, max_retry_wait=args.max_retry_wait)
        resolved = []
        for index, record in enumerate(records, 1):
            if not args.refresh and re.fullmatch(r'spotify:track:[A-Za-z0-9]{22}', record.get('uri') or ''):
                resolved.append(record)
                log(f'[{index}/{len(records)}] Reusing {record["artist"]} - {record["track_title"]}')
                continue
            started = time.monotonic()
            log(f'[{index}/{len(records)}] Looking up {record["artist"]} - {record["track_title"]}')
            track = resolve(record, spotify)
            resolved.append(track)
            log(f"[{index}/{len(records)}] {track['match_status']} ({time.monotonic() - started:.1f}s)")
        temporary = args.output.with_suffix(args.output.suffix + '.tmp')
        temporary.write_text(json.dumps(resolved, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temporary.replace(args.output)
        playable = sum(bool(track.get('uri')) for track in resolved)
        log(f'Saved {len(resolved)} tracks to {args.output}: {playable} resolved, {len(resolved) - playable} unresolved.')
    except (ValueError, OSError, requests.RequestException, KeyError) as error:
        log(f'Lookup failed: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
