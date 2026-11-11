# Cyberpunk 2077 Radioport

A Cyberpunk-inspired radio HUD with Spotify playback. Built with one HTML file containing all interface CSS and JavaScript, plus a generated station catalog. No frontend build or npm installation is required. Orbitron loads from Google Fonts.

<img width="1919" height="1080" alt="image" src="https://github.com/user-attachments/assets/35254b96-982c-417c-aad3-b5524141699b" />


## Run locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. Serve the folder over HTTP; opening `index.html` directly prevents JSON loading in most browsers.

## Controls

| Key / button | Action |
| --- | --- |
| ↑ / ↓ | Move the station cursor |
| F / Enter | Select a station |
| A / Previous | Previous song in the current channel |
| D / Next | Next song in the current channel |
| Space / Play-Pause | Toggle playback |
| C / Escape | Close the HUD |
| F when closed | Reopen the HUD |
| Spotify icon | Show/hide the embedded Spotify player |

Station rows are clickable. Space works with the menu closed; focused buttons retain their standard keyboard behavior. Track navigation wraps at either end and automatically starts the selected song. Finished songs advance through the active channel and loop. Manual pause remains available.

The last channel and each channel's last track are saved locally in your browser. Refresh restores the same song from its beginning, not its previous timestamp. A removed track falls back to the channel's first playable song.

The album cover shows a loading indicator during connection or buffering, with a vignette and hover dimming. Channels without artwork use a station emblem. Previous/next controls and their A/D hints sit beside TRACK. Play/Pause and Spotify controls sit at the bottom left, with a Space keycap under Play/Pause.

## Resolve the full song catalog

The frontend needs no API secret. The optional Python lookup requires a Spotify developer app's client ID and secret, configured only in your terminal:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SPOTIFY_CLIENT_ID='your-client-id'
export SPOTIFY_CLIENT_SECRET='your-client-secret'
python scripts/lookup_tracks.py tracks.catalog.json
```

**Use `tracks.catalog.json` for the full catalog.** The script reads environment variables; it does not automatically load `.env` files.

The script prints immediate startup, authentication, per-track progress, search results, and rate-limit waits to stderr. Each HTTP request has a 30-second timeout; a track can require several searches. Restart a running process to load script changes.

The script updates `tracks.catalog.json` in place, preserving station/source fields and replacing Spotify lookup metadata. Review `review`, `low_confidence`, and `not_found` entries afterward. To review in a separate file first, pass `-o tracks.resolved.json`.

Existing valid Spotify URIs are reused by default; pass `--refresh` to re-query them. Search requests are paced by 0.5 seconds. On HTTP 429 the script honors the full Retry-After delay. If the delay exceeds 60 seconds it stops without replacing the catalog, prints the requested cooldown, and sends no retry. Wait for that cooldown before rerunning, or explicitly allow a longer automatic wait with `--max-retry-wait SECONDS`.

The output file is replaced on a successful run. A failed lookup preserves the prior output. Never commit Spotify client secrets or put them in HTML/JSON. `.gitignore` excludes local environment files, virtual environments, caches, and temporary files.

JSON input accepts `station_num`, `station_name`, `track_title` (or `title`), and `artist`. The catalog uses the source Artist column for display and retains Performed by in `performed_by`; lookup searches both credits, including parenthesized and featured performers. Multiple songs with the same station are grouped into a looping channel playlist. Output adds `uri`, `spotify_track_name`, `album_artwork_url`, `match_status`, and optional `match_score`. Unresolved songs are skipped during playback.

Plain text input supports one `Artist - Track Title` per line, blank lines, and `#` comments:

```sh
python scripts/lookup_tracks.py tracks.txt --station-num 89.7 --station-name 'GROWL FM' -o tracks.resolved.json
```

## Publish on GitHub Pages

1. Push this folder to a GitHub repository, including `index.html` and `tracks.catalog.json`.
2. Open the repository's **Settings → Pages**.
3. Choose **Deploy from a branch**, select your branch (usually `main`) and **/(root)**, then save.
4. Open the published URL shown by GitHub after deployment completes.

No build command, Python server, or Spotify API secret is needed on the host. The Python script is a local tool for preparing the JSON before publication. See [GitHub's publishing instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Spotify playback limits

Uses the official [Spotify iframe API](https://developer.spotify.com/documentation/embeds/references/iframe-api). Playback events supply a URI and playback state; song metadata comes from `tracks.catalog.json`. The player stays clipped until the Spotify icon is clicked.

The app requests autoplay on startup and every song change. Browsers or Spotify can still block playback or limit it to a preview. Reveal the player, sign in if prompted, and press Play if needed. Uninterrupted/full playback cannot be guaranteed by this app. The iframe API has no volume setter; use Spotify or system volume controls.

## Data and files

- `index.html`: interface and playback logic.
- `tracks.catalog.json`: the single input/runtime catalog, with 197 unique songs imported from `song-refs.md` plus retained Spotify metadata.
- `song-refs.md`: user-supplied IGN HTML tables (198 rows, including Run twice).
- `scripts/import_song_refs.py`: rebuilds the catalog from those tables and retains metadata for matching entries.
- `scripts/lookup_tracks.py`: Spotify search and metadata lookup.
- `tests/`: Python lookup and JavaScript playback tests.

Direct IGN access returned HTTP 403. The current catalog instead comes from the user-provided IGN HTML in `song-refs.md`, replacing the earlier fallback source. All source names and credits are preserved; duplicate Run in Night FM is listed once. Source typos and Spotify title differences may still require search adjustments. Rebuild with `python3 scripts/import_song_refs.py`, then run the lookup to resolve changed entries. Backgrounds and station graphics are original approximations. This is an unofficial fan project, unaffiliated with CD PROJEKT RED or Spotify.

## Checks

With the Python dependencies installed:

```sh
node --test tests/playback.test.cjs
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m py_compile scripts/lookup_tracks.py
```

## Track count discrepancies

The track counter shows resolved Spotify songs; unresolved catalog entries are skipped. Hover the counter to see resolved versus listed totals. Inspect `match_status` and `uri` in `tracks.catalog.json` for unresolved songs. The catalog now follows the supplied IGN HTML, including Pig Dinner and the reference’s revised names and credits. Re-run the updated lookup to retry artist aliases and combined performer credits. The original `stations.json` file was removed after merging its lookup metadata into `tracks.catalog.json`.
