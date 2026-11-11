import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('import_refs', ROOT / 'scripts/import_song_refs.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReferenceImportTests(unittest.TestCase):
    def test_reference_catalog_matches_all_unique_source_rows(self):
        records, duplicates = module.import_records((ROOT / 'song-refs.md').read_text(), [])
        catalog = json.loads((ROOT / 'tracks.catalog.json').read_text())
        self.assertEqual(len(records), 197)
        self.assertEqual(len({r['station_num'] for r in records}), 14)
        self.assertEqual([r['track_title'] for r in duplicates], ['Run'])
        for expected, actual in zip(records, catalog, strict=True):
            for field in ('station_num', 'station_name', 'track_title', 'artist', 'performed_by'):
                self.assertEqual(actual[field], expected[field])

    def test_preserves_metadata_only_for_matching_identity(self):
        html = '<h2>88.9 Pacific Dreams</h2><table><tr><td>Song</td><td>Band</td><td>Performer</td></tr></table>'
        old = [{'station_num':'88.9','track_title':'Song','artist':'Performer','in_game_artist':'Band','uri':'spotify:track:kept'}]
        records, _ = module.import_records(html, old)
        self.assertEqual(records[0]['uri'], 'spotify:track:kept')
        changed, _ = module.import_records(html.replace('<td>Band</td>', '<td>Other Band</td>'), old)
        self.assertIsNone(changed[0]['uri'])

    def test_invalid_reference_does_not_produce_empty_catalog(self):
        with self.assertRaises(ValueError):
            module.import_records('<html>No tables</html>', [])
