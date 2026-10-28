# YouTube Downloader Application

A CLI tool for downloading YouTube videos, metadata, and transcripts using yt-dlp. Automatically converts subtitles to deduplicated text and live chat to CSV.

## Features

- Download video with best-quality audio+video (merged to MP4).
- Download subtitles (English) and live chat, automatically converted to text and CSV.
- Deduplicate transcript lines after conversion.
- Extract comments to CSV (opt-in).
- `--metadata-only`: skip the video download and fetch subtitles, live chat, description, info JSON, and optionally comments.
- `--transcript-only`: download and convert subtitles only.
- `--comments-only`: download comments only, extracted straight to CSV.
- Optional Firefox cookie support for authenticated downloads.
- FFmpeg availability warning when merging streams.
- All output saved to a timestamped `outputN/` folder.

## Project Structure

```text
youtube-downloader-app
├── src
│   ├── main.py                 # CLI entry point (click)
│   ├── downloader.py           # yt-dlp download logic
│   ├── extract_comments.py     # Extract comments from info.json to CSV
│   ├── livechat_to_csv.py      # Convert live chat NDJSON to CSV
│   ├── vtt_to_text.py          # Convert VTT subtitle files to plain text
│   ├── remove_dupe_lines.py    # Deduplicate transcript lines
│   ├── firefox_cookie_export.py # Export Firefox cookies for yt-dlp
│   ├── kick_live_downloader.py # Kick.com live stream downloader (Playwright + ffmpeg)
│   └── kick_vod_downloader.py  # Kick.com VOD + chat downloader
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

Tools for analysing the downloaded files (chat filtering, sentiment, `vod_offset` backfill, timestamp conversion) are in [`youtube-study/analysis/`](../youtube-study/analysis/README.md). See [Analysing Kick chat](#analysing-kick-chat).

## Installation

1. Clone the repository:

   ```zsh
   git clone <repository-url>
   cd youtube-downloader-app
   ```

2. Install the required dependencies:

   ```zsh
   pip install -r requirements.txt
   ```

3. Install [FFmpeg](https://ffmpeg.org/download.html) for merging audio and video streams into a single MP4 file.

4. Build the YouTube PO token generation script (one-time). YouTube now requires a
   "PO token" to serve video data; without one, downloads fail with
   `ERROR: unable to download video data: HTTP Error 403: Forbidden` even though the
   format listing works. The [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider)
   plugin (installed via `requirements.txt`) generates tokens automatically, but it
   also needs its generation script cloned and built at the default location in your
   home directory (requires Node.js ≥ 20):

   ```zsh
   git clone --depth 1 --branch 1.3.1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git ~/bgutil-ytdlp-pot-provider
   cd ~/bgutil-ytdlp-pot-provider/server
   npm ci && npx tsc
   ```

   yt-dlp finds the script there automatically — no configuration or code changes
   needed. A per-run warning about `http://127.0.0.1:4416` being unreachable is
   harmless: it is the plugin probing for its optional server mode before falling
   back to the script.

## Usage

```zsh
python src/main.py [OPTIONS] "URL"
```

> **Note:** Always quote the URL in zsh or bash. The `?` in a YouTube URL (e.g. `?v=...`) is a glob wildcard in the shell — without quotes, the shell tries to expand it against local files and prints `no matches found` before Python runs.

### Options

| Option | Description |
| --- | --- |
| `--cookies` | Use cookies from Firefox for authenticated downloads |
| `--comments` | Download and extract comments to CSV |
| `--metadata-only` | Skip video; fetch subtitles, live chat, description, info JSON, and convert |
| `--transcript-only` | Download subtitles only and convert to deduplicated text |
| `--comments-only` | Download comments only (no video/subtitles/live chat); extract to CSV (info JSON kept) |
| `--video-only` | (Kick VOD only) Download video only, skip chat |
| `--chat-only` | (Kick VOD only) Download chat only, skip video |
| `--chat-delay N` | (Kick VOD only) Milliseconds between chat API requests (default: 300, min: 100) |
| `--sabr` | (YouTube full-download or `--comments-only` mode) **Fallback, normally not needed since yt-dlp 2026.08.19.** Download via the SABR dev build of yt-dlp in `venv-sabr` — only if a regular download 403s or dies after a few hundred KB again. Slower (YouTube paces delivery) and briefly opens a minimized Chrome window. Setup: see "SABR downloads" below |
| `--sabr-comments-only` | Shorthand for `--sabr --comments-only`: fetch comments only via `venv-sabr` (same fallback status as `--sabr`) |
| `--help` | Show help message and exit |

### Examples

Download a video (default — no comments):

```zsh
python src/main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download with comments:

```zsh
python src/main.py --comments "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download everything except the video (metadata, subtitles, live chat, comments):

```zsh
python src/main.py --metadata-only --comments "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download and convert transcript only:

```zsh
python src/main.py --transcript-only "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download comments only (output folder will contain `<title>_comments.csv` plus the raw `.info.json`, kept for debugging or re-extracting the CSV later):

```zsh
python src/main.py --comments-only "https://www.youtube.com/watch?v=VIDEO_ID"
```

`--metadata-only`, `--transcript-only`, and `--comments-only` are mutually exclusive. Of the three, only `--comments-only` can be combined with `--sabr` (see [SABR downloads](#sabr-downloads---sabr)).

> **Live chat vs. comments:** there is no conflict between the two — live chat is saved to its own `.live_chat.json` file while comments live inside `.info.json`, so downloading a video with `--comments` fetches both (for videos that have both, e.g. finished live streams). In practice most videos only *have* one or the other: live chat exists only for live streams/premieres, and comments are unavailable while a stream is still live.

Use Firefox cookies for a members-only or age-restricted video:

```zsh
python src/main.py --cookies "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download a Kick live stream (tries yt-dlp, falls back to Playwright + ffmpeg automatically):

```zsh
python src/main.py "https://kick.com/username"
```

Download a Kick VOD with full chat history:

```zsh
python src/main.py "https://kick.com/username/videos/UUID"
```

Download a Kick VOD video only (skip chat):

```zsh
python src/main.py --video-only "https://kick.com/username/videos/UUID"
```

## SABR downloads (`--sabr`)

**Status (2026-10-27): a fallback you should rarely need.** Between 2026-08-02 and
2026-08-19, YouTube required PO tokens for nearly all direct media URLs and, on distrusted
IPs (VPN exits, datacenters), served only the first few hundred KB of the remaining
`android_vr` URLs before returning 403 — even with the PO token plugin installed. YouTube
killed the `android_vr` client outright on 2026-08-17, and yt-dlp 2026.08.19 replaced it
with the `visionos` client (2026.10.21 added `tv_samsung` as a default too). Those clients
serve whole files again: verified on 2026-10-27 with stable yt-dlp 2026.10.26 on a
commercial VPN exit — a full 4K download, subtitles, and the comments API all worked
through the normal `python src/main.py "<url>"` path with no `--sabr`. Keep the main venv's
yt-dlp current (`pip install -U yt-dlp`) before reaching for this section.

YouTube's own SABR streaming protocol is not subject to the per-URL cap, so `--sabr` stays
available in case the cap returns. yt-dlp's SABR support is still an unmerged dev build
([PR #13515](https://github.com/yt-dlp/yt-dlp/pull/13515), open as of 2026-10-25), so it
lives in a **separate virtualenv** (`venv-sabr`, gitignored) and is only used when you pass
`--sabr`; the pinned stable yt-dlp is untouched.

One-time setup (repo root; Google Chrome must be installed):

```zsh
python -m venv venv-sabr
venv-sabr/bin/pip install "yt-dlp[default,curl-cffi] @ git+https://github.com/yt-dlp/yt-dlp.git@refs/pull/13515/head" yt-dlp-getpot-wpc
```

The PR head is rebased on master periodically, so re-run the `pip install` line to refresh
an old `venv-sabr` (a build from before 2026-08-19 predates the client changes above). The
maintainer also publishes a prebuilt
[`sabr` pre-release](https://github.com/bashonly/yt-dlp/releases/tag/sabr) of the same branch.

Then:

```zsh
python src/main.py --sabr "https://www.youtube.com/watch?v=VIDEO_ID"
```

To fetch only comments through `venv-sabr` (e.g. when `--comments-only` fails on a VPN IP),
use `--sabr --comments-only` or the `--sabr-comments-only` shorthand. It skips the media
entirely (no format selection is required) and writes `<title>.info.json` plus
`<title>_comments.csv`, the same output as `--comments-only`:

```zsh
python src/main.py --sabr-comments-only "https://www.youtube.com/watch?v=VIDEO_ID"
```

Notes:

- **Token provider:** SABR video streams re-validate the PO token mid-stream and reject
  the synthetic tokens from `bgutil-ytdlp-pot-provider` (downloads die at ~5 MB with
  "This stream requires a GVS PO Token to continue"). `venv-sabr` therefore uses
  [yt-dlp-getpot-wpc](https://github.com/coletdjnz/yt-dlp-getpot-wpc) instead, which
  mints browser-attested tokens by driving a **logged-out, throwaway Chrome instance**
  (fresh temporary profile, cookies cleared, loads only youtube.com). Do not install
  the bgutil plugin in `venv-sabr` — it outranks wpc and breaks video downloads.

- A minimized Chrome window appears during downloads — that's wpc; don't close it.
- Downloads are slower than normal: YouTube paces SABR delivery (a 720p feature-length
  video can take an hour).

- **Known issue:** `nodriver` 0.50.3 (a wpc dependency) ships a non-UTF-8 byte in
  `cdp/network.py` that breaks the plugin with `SyntaxError: Non-UTF-8 code`
  (upstream bug: [nodriver#35](https://github.com/ultrafunkamsterdam/nodriver/issues/35),
  open since 2026-03). Fix by re-encoding the file once:
  `python -c "import pathlib; p = pathlib.Path('venv-sabr/lib/python3.14/site-packages/nodriver/cdp/network.py'); p.write_bytes(p.read_bytes().decode('latin-1').encode('utf-8'))"`

- **TODO (check back after 2027-01):** PR #13515 was still open on 2026-10-25 (the
  maintainer called it a large, lower-priority review on 2026-08-21). When it merges into
  stable yt-dlp, fold SABR into the normal flow and retire `venv-sabr`. Since regular
  downloads work again (see status above), the flag could also simply be removed if the
  cap hasn't returned by then.

## Downloading a channel

To download all videos in a channel, pass a channel URL instead of a single video URL:

```txt
https://www.youtube.com/@ChannelName
https://www.youtube.com/channel/UCxxxxxxxxx
```

yt-dlp handles channel URLs natively and will iterate over every video in the channel.

### Channel download support by feature

| Feature | Channel support |
| --- | --- |
| Video download | Works for all videos |
| Subtitles/VTT | Works for all videos |
| Live chat | Works for all videos |
| Comments CSV | **Last video only** |

### Comments limitation

When downloading a channel, comment extraction only processes a single `.info.json` file (the most recently created one). All other per-video `.info.json` files are ignored, so comments are only extracted for the last video downloaded.

> **Recommendation:** Do not enable `--comments` when downloading a channel or multiple videos. Download comments for individual videos instead.

## Kick.com

### Live streams — `main.py`

Pass a Kick channel URL to `main.py`. yt-dlp is tried first; if it fails, the download falls back automatically to `kick_live_downloader.py` (Playwright + ffmpeg with m3u8 auto-detection):

```zsh
python src/main.py "https://kick.com/username"
```

If the automated fallback also fails (e.g. Cloudflare blocks the headless browser), run `kick_live_downloader.py` directly. The recommended approach is to supply the m3u8 URL manually — this is the most reliable method as it bypasses Cloudflare entirely:

```zsh
python src/kick_live_downloader.py --page "https://kick.com/username" --m3u8 "https://..."
```

**Getting the m3u8 URL** (quickest way):

1. Open the Kick channel in your browser with the stream playing
2. Open DevTools → **Network** tab → filter by `m3u8`
3. Reload the page — a `master.m3u8` request will appear
4. Right-click it → **Copy** → **Copy URL**

If you don't want to grab it manually, `--headful` opens a visible browser to let you complete any Cloudflare verification, then auto-detects the m3u8:

```zsh
python src/kick_live_downloader.py --page "https://kick.com/username" --headful
```

### VOD replays

Downloads a VOD and its full chat history. Requires only the VOD URL — metadata, `channel_id`, and stream timestamps are resolved automatically.

You can use either `main.py` (unified entry point) or `kick_vod_downloader.py` directly:

```zsh
# Via main.py (recommended)
python src/main.py [OPTIONS] "URL"

# Or directly
python src/kick_vod_downloader.py [OPTIONS] "URL"
```

`URL` must be a Kick VOD URL containing a UUID:

```text
https://kick.com/username/videos/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Both Kick video ID formats are accepted: legacy UUIDs (v4) are used directly, and new-style UUIDs (v7, as shown in Kick's current frontend URLs — they start with the timestamp, e.g. `019f...`) are resolved automatically via the channel's videos listing. Because that listing only returns a channel's 30 most recent VODs, a new-style URL for an older VOD cannot be resolved — the script will say so explicitly.

The video is downloaded from the direct HLS playlist (`source` in the VOD metadata), not through yt-dlp's Kick extractor, because that extractor (yt-dlp ≥ 2026.10.26) only accepts new-style IDs. The script prints `Video source: HLS playlist ...` so you can see which path it took.

| Option | Description |
| --- | --- |
| `--video-only` | Download video only, skip chat |
| `--chat-only` | Download chat only, skip video |
| `--chat-delay N` | Milliseconds between chat API requests (default: 300, min: 100) |

#### Examples via main.py (recommended)

```zsh
# Video + full chat (default)
python src/main.py "https://kick.com/username/videos/UUID"

# Chat only
python src/main.py --chat-only "https://kick.com/username/videos/UUID"

# Video only
python src/main.py --video-only "https://kick.com/username/videos/UUID"
```

#### Examples via kick_vod_downloader.py (direct)

```zsh
# Same options and behaviour
python src/kick_vod_downloader.py "https://kick.com/username/videos/UUID"
```

Output is written to a new `kick_outputN/` folder:

| File | Contents |
| --- | --- |
| `metadata.json` | Raw VOD metadata from the Kick API |
| `<title>_chat.csv` | Chat messages (vod_offset, timestamp, username, user_id, message, type, badges, color, amount, message_id, metadata) |
| `<title>_chat.ndjson` | Raw chat messages, one JSON object per line |
| `<title>.mp4` | Downloaded video (unless `--chat-only`) |

The `vod_offset` column is formatted as `H:MM:SS` and gives the playback position in the downloaded video where each message appears — computed as `message_timestamp − vod_start_time`. Chat messages include emotes as `[emote:ID:name]` tokens. The `duration` field unit (seconds vs. milliseconds) is auto-detected. Increase `--chat-delay` if you encounter `429` rate-limit responses.

### Analysing Kick chat

The `<title>_chat.csv` above is the input for the analysis scripts in [`youtube-study/analysis/`](../youtube-study/analysis/README.md). They moved out of `src/` on 2026-06-30, so run them from there:

| Script | Use it to |
| --- | --- |
| `kick-csv-analysis.py` | Score chat sentiment over the VOD timeline, rank users, and check for bots. See the [walkthrough](../youtube-study/analysis/README.md#walkthrough-analysing-a-kick-chat). |
| `filter_chat.py` | Remove emote-only, copy-paste, and reaction-flood noise |
| `add_vod_offset.py` | Add the `vod_offset` column to a `_chat.csv` downloaded before that column existed |
| `timestamp_converter.py` | Convert between EST times and Unix timestamps |

## Opening chat CSVs safely

Chat messages and usernames are written to the CSVs verbatim. A message that starts with `=`, `+`, `-`, or `@` can be interpreted as a live formula if the file is opened directly in Excel or another spreadsheet app (CSV/formula injection). Open these files in a text editor or load them with pandas/Python instead — or, in a spreadsheet, import the columns as **text** rather than opening the file directly.

## Dependencies

- `yt-dlp`: Download videos from YouTube and other sites.
- `click`: CLI framework.
- `pytz`: Timezone calculations.
- `browser-cookie3`: Read cookies from the browser for authenticated downloads.
- `playwright`: Headless Firefox for the Kick live stream fallback (`playwright install firefox` required after pip install).
- `requests`: Kick API calls.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Generated by AI

*Text generated by AI.*
