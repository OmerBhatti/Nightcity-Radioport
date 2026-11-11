import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('lookup', Path(__file__).parents[1] / 'scripts/lookup_tracks.py')
lookup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lookup)


class LookupTests(unittest.TestCase):
    def test_text_preserves_hyphens_in_title(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'tracks.txt'
            path.write_text('# comment\nArtist - A - B\n', encoding='utf-8')
            self.assertEqual(lookup.read_tracks(path, '89.7', 'GROWL FM')[0]['track_title'], 'A - B')

    def test_invalid_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'tracks.json'
            path.write_text('[{"artist":"A"}]')
            with self.assertRaises(ValueError):
                lookup.read_tracks(path)

    def test_no_match_keeps_null_uri(self):
        class FakeSpotify:
            def search(self, query):
                return []
        self.assertIsNone(lookup.resolve({'artist':'A','track_title':'B'}, FakeSpotify())['uri'])

    def test_matching_track_extracts_artwork(self):
        class FakeSpotify:
            def search(self, query):
                return [{'name':'Song','artists':[{'name':'Artist'}], 'uri':'spotify:track:example',
                         'album':{'images':[{'url':'https://example.com/art.jpg'}]}}]
        result = lookup.resolve({'artist':'Artist','track_title':'Song'}, FakeSpotify())
        self.assertEqual(result['match_status'], 'matched')
        self.assertEqual(result['album_artwork_url'], 'https://example.com/art.jpg')


if __name__ == '__main__':
    unittest.main()
