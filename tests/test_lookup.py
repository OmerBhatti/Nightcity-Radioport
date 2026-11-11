import importlib.util
import io
from contextlib import redirect_stderr
from unittest.mock import Mock, patch
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

class MatchingRegressionTests(unittest.TestCase):
    @staticmethod
    def track(name, artist, uri='spotify:track:test'):
        return {'name': name, 'artists': [{'name': artist}], 'uri': uri, 'album': {'images': []}}

    def test_retries_alias_after_unrelated_initial_results(self):
        wrong = self.track('Isometric Air', 'Unrelated Artist', 'spotify:track:wrong')
        right = self.track('Isometric Air', 'Quantum Lovers', 'spotify:track:right')
        class FakeSpotify:
            def search(self, query):
                return [right] if 'artist:Quantum Lovers' in query else [wrong]
        result = lookup.resolve({'track_title':'Isometric Air','artist':'Brian Aspey',
                                 'in_game_artist':'Quantum Lovers'}, FakeSpotify())
        self.assertEqual(result['uri'], 'spotify:track:right')

    def test_multi_artist_credit_matches_individual_spotify_artist(self):
        track = self.track('Fumes', 'Aleyna Moon')
        class FakeSpotify:
            def search(self, query):
                return [track]
        result = lookup.resolve({'track_title':'Fumes','artist':'Aleyna Moon and Shrinjay Ghosh'}, FakeSpotify())
        self.assertEqual(result['match_status'], 'matched')

    def test_artist_match_alone_cannot_accept_wrong_song(self):
        track = self.track('Completely Different Recording', 'Artist')
        class FakeSpotify:
            def search(self, query):
                return [track]
        result = lookup.resolve({'track_title':'Song','artist':'Artist'}, FakeSpotify())
        self.assertIsNone(result['uri'])

    def test_read_tracks_preserves_alias_for_matching(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'tracks.json'
            path.write_text('[{"track_title":"Song","artist":"Artist","in_game_artist":"Alias"}]')
            self.assertEqual(lookup.read_tracks(path)[0]['in_game_artist'], 'Alias')


    def test_source_performed_by_credit_supplies_search_variants(self):
        variants = lookup.artist_variants({'artist':'Keine','performed_by':'SRDD (Sebastian Roberston; Daniel Davies)'})
        for name in ('Keine', 'SRDD', 'Sebastian Roberston', 'Daniel Davies'):
            self.assertIn(name, variants)
        featured = lookup.artist_variants({'artist':'Kyubik','performed_by':'Konrad OldMoney (ft. Johnny GR4VES)'})
        self.assertIn('Konrad OldMoney', featured)
        self.assertIn('Johnny GR4VES', featured)


class ProgressTests(unittest.TestCase):
    def test_authentication_is_logged_before_waiting_for_response(self):
        output = io.StringIO()
        spotify = lookup.Spotify('test-id', 'test-secret')
        def request(*args, **kwargs):
            self.assertIn('Authenticating with Spotify', output.getvalue())
            raise lookup.requests.Timeout('simulated timeout')
        with redirect_stderr(output), patch.object(spotify.session, 'post', side_effect=request):
            with self.assertRaises(lookup.requests.Timeout):
                spotify.search('Song')
        self.assertNotIn('test-secret', output.getvalue())

    def test_startup_and_track_progress_are_logged_before_resolving(self):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.json'
            target = Path(directory) / 'output.json'
            source.write_text('[{"artist":"Artist","track_title":"Song"}]')
            def resolve(record, spotify):
                self.assertIn('Loaded 1 tracks', output.getvalue())
                self.assertIn('[1/1] Looking up Artist - Song', output.getvalue())
                return {**record, 'uri': None, 'match_status': 'not_found'}
            with redirect_stderr(output), patch.object(lookup.sys, 'argv', ['lookup', str(source), '-o', str(target)]), patch.dict(lookup.os.environ, {'SPOTIFY_CLIENT_ID':'test-id','SPOTIFY_CLIENT_SECRET':'test-secret'}), patch.object(lookup, 'resolve', side_effect=resolve):
                self.assertEqual(lookup.main(), 0)
            self.assertIn('Saved 1 tracks', output.getvalue())


class RateLimitTests(unittest.TestCase):
    def test_long_retry_after_stops_without_retrying_early(self):
        spotify = lookup.Spotify('id', 'secret')
        spotify.expires = float('inf')
        response = Mock(status_code=429, headers={'Retry-After':'3600'})
        with redirect_stderr(io.StringIO()), patch.object(spotify.session, 'get', return_value=response) as get, patch.object(lookup.time, 'sleep') as sleep:
            with self.assertRaisesRegex(lookup.requests.RequestException, 'Retry-After is 3600s'):
                spotify.search('Song')
            self.assertEqual(get.call_count, 1)
            sleep.assert_called_once_with(0.5)

    def test_short_retry_after_is_honored_in_full(self):
        spotify = lookup.Spotify('id', 'secret')
        spotify.expires = float('inf')
        limited = Mock(status_code=429, headers={'Retry-After':'45'})
        success = Mock(status_code=200)
        success.json.return_value = {'tracks':{'items':[]}}
        with redirect_stderr(io.StringIO()), patch.object(spotify.session, 'get', side_effect=[limited,success]), patch.object(lookup.time, 'sleep') as sleep:
            self.assertEqual(spotify.search('Song'), [])
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5,30,15,0.5])

    def test_existing_resolved_track_is_reused_without_search(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.json'
            target = Path(directory) / 'output.json'
            source.write_text('[{"artist":"Artist","track_title":"Song","uri":"spotify:track:AAAAAAAAAAAAAAAAAAAAAA"}]')
            with redirect_stderr(io.StringIO()), patch.object(lookup.sys, 'argv', ['lookup',str(source),'-o',str(target)]), patch.dict(lookup.os.environ, {'SPOTIFY_CLIENT_ID':'id','SPOTIFY_CLIENT_SECRET':'secret'}), patch.object(lookup, 'resolve') as resolve:
                self.assertEqual(lookup.main(), 0)
                resolve.assert_not_called()
            self.assertIn('spotify:track:AAAAAAAAAAAAAAAAAAAAAA', target.read_text())


if __name__ == '__main__':
    unittest.main()
