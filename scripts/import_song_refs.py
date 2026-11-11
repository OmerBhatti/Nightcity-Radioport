#!/usr/bin/env python3
"""Import saved IGN HTML tables into the runtime catalog without network access."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata

SOURCE_URL = 'https://www.ign.com/wikis/cyberpunk-2077/All_Radio_Stations_and_Songs'
METADATA = ('uri', 'spotify_track_name', 'spotify_artists', 'album_artwork_url',
            'match_status', 'match_score')


def normalized(value):
    text = unicodedata.normalize('NFKD', value.casefold())
    return re.sub(r'[^\w]+', ' ', ''.join(
        char for char in text if not unicodedata.combining(char))).strip()


class ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = None
        self.parts = []
        self.station = None
        self.row = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        if tag in ('h2', 'td', 'th'):
            self.capture, self.parts = tag, []
        elif tag == 'br' and self.capture:
            self.parts.append('; ')
        if tag == 'tr':
            self.row = []

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            text = ' '.join(''.join(self.parts).split())
            if tag == 'h2':
                match = re.fullmatch(r'(\d{2,3}\.\d)\s+(.+)', text)
                self.station = match.groups() if match else None
            else:
                self.row.append(text)
            self.capture = None
        if tag == 'tr' and self.station and self.row and self.row != ['Song', 'Artist', 'Performed by']:
            if len(self.row) != 3 or not all(self.row):
                raise ValueError(f'Incomplete song row: {self.row!r}')
            title, artist, performer = self.row
            self.records.append({'station_num': self.station[0],
                                 'station_name': self.station[1],
                                 'track_title': title, 'artist': artist,
                                 'in_game_artist': artist, 'performed_by': performer,
                                 'source_url': SOURCE_URL, 'source_file': 'song-refs.md'})


def import_records(html, previous):
    parser = ReferenceParser()
    parser.feed(html)
    if not parser.records:
        raise ValueError('No station song tables found; existing catalog was not changed.')
    key = lambda record: (record['station_num'], normalized(record['track_title']),
                          normalized(record.get('in_game_artist', record['artist'])))
    old = {key(record): record for record in previous}
    seen, result, duplicates = set(), [], []
    for record in parser.records:
        identity = key(record)
        if identity in seen:
            duplicates.append(record)
            continue
        seen.add(identity)
        metadata = old.get(identity, {})
        output = {**record, 'uri': None, 'spotify_track_name': None,
                  'album_artwork_url': None, 'match_status': 'not_searched'}
        output.update({field: metadata[field] for field in METADATA if field in metadata})
        result.append(output)
    return result, duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path, nargs='?', default=Path('song-refs.md'))
    parser.add_argument('-o', '--output', type=Path, default=Path('tracks.catalog.json'))
    args = parser.parse_args()
    previous = json.loads(args.output.read_text()) if args.output.exists() else []
    records, duplicates = import_records(args.reference.read_text(), previous)
    temporary = args.output.with_suffix(args.output.suffix + '.tmp')
    temporary.write_text(json.dumps(records, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(args.output)
    print(f'Imported {len(records)} unique songs across {len({r["station_num"] for r in records})} stations.')
    print(f'Skipped {len(duplicates)} duplicate rows; preserved {sum(bool(r.get("uri")) for r in records)} Spotify URIs.')


if __name__ == '__main__':
    main()
