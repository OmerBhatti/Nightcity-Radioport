#!/usr/bin/env python3
"""Resolve JSON records or 'artist - title' text lines to Spotify tracks."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from difflib import SequenceMatcher

import requests


class Spotify:
    def __init__(self, client_id, client_secret):
        self.session = requests.Session()
        self.credentials = (client_id, client_secret)
        self.token = None
        self.expires = 0

    def search(self, query):
        if time.monotonic() >= self.expires:
            response = self.session.post(
                'https://accounts.spotify.com/api/token', auth=self.credentials,
                data={'grant_type': 'client_credentials'}, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.token = data['access_token']
            self.expires = time.monotonic() + data['expires_in'] - 60
        for attempt in range(4):
            response = self.session.get(
                'https://api.spotify.com/v1/search',
                headers={'Authorization': f'Bearer {self.token}'},
                params={'q': query, 'type': 'track', 'limit': 10}, timeout=30)
            if response.status_code == 429 and attempt < 3:
                time.sleep(min(float(response.headers.get('Retry-After', '1')), 120))
                continue
            response.raise_for_status()
            return response.json()['tracks']['items']


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
        result.append({'station_num': str(record.get('station_num', station_num)),
                       'station_name': str(record.get('station_name', station_name)),
                       'track_title': title.strip(), 'artist': artist.strip()})
    return result


def similarity(a, b):
    return SequenceMatcher(None, a.casefold(), b.casefold()).ratio()


def resolve(record, spotify):
    title, artist = record['track_title'], record['artist']
    candidates = spotify.search(f'track:{title} artist:{artist}')
    if not candidates:
        candidates = spotify.search(f'{title} {artist}')
    def score(track):
        return (similarity(title, track['name']) + max(
            (similarity(artist, a['name']) for a in track['artists']), default=0)) / 2
    best = max(candidates, key=score) if candidates else None
    output = {**record, 'uri': None, 'spotify_track_name': None,
              'album_artwork_url': None, 'match_status': 'not_found'}
    if best:
        confidence = score(best)
        output['match_score'] = round(confidence, 3)
        if confidence >= 0.65:
            images = best.get('album', {}).get('images', [])
            output.update(uri=best['uri'], spotify_track_name=best['name'],
                          album_artwork_url=images[0]['url'] if images else None,
                          match_status='matched' if confidence >= 0.85 else 'review')
        else:
            output['match_status'] = 'low_confidence'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=Path('stations.json'))
    parser.add_argument('--station-num', default='')
    parser.add_argument('--station-name', default='RADIOPORT')
    args = parser.parse_args()
    try:
        records = read_tracks(args.input, args.station_num, args.station_name)
        client_id, secret = os.getenv('SPOTIFY_CLIENT_ID'), os.getenv('SPOTIFY_CLIENT_SECRET')
        if not client_id or not secret:
            raise ValueError('Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.')
        spotify = Spotify(client_id, secret)
        resolved = []
        for record in records:
            track = resolve(record, spotify)
            resolved.append(track)
            print(f"{track['match_status']}: {track['artist']} - {track['track_title']}", file=sys.stderr)
        temporary = args.output.with_suffix(args.output.suffix + '.tmp')
        temporary.write_text(json.dumps(resolved, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temporary.replace(args.output)
    except (ValueError, OSError, requests.RequestException, KeyError) as error:
        print(f'Lookup failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
