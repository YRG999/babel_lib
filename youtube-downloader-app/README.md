# YouTube Downloader Application

A CLI tool for downloading YouTube videos, metadata, and transcripts using yt-dlp. Automatically converts subtitles to deduplicated text and live chat to CSV.

## Features

- Download video with best-quality audio+video (merged to MP4).
- Download subtitles (English) and live chat, automatically converted to text and CSV.
- Deduplicate transcript lines after conversion.
- Extract comments to CSV (opt-in).
- `--metadata-only`: skip the video download and fetch subtitles, live chat, description, info JSON, and optionally comments.
- `--transcript-only`: download and convert subtitles only.
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
│   ├── kick_vod_downloader.py  # Kick.com VOD + chat downloader
│   ├── timestamp_converter.py  # EST/epoch timestamp converter utility
│   ├── add_vod_offset.py       # Backfill vod_offset column in existing Kick VOD chat CSVs
│   ├── filter_chat.py          # Filter emote-only, repetitive, and reaction-flood messages from chat CSVs
│   └── comments.py             # Legacy comment helpers (unused by main.py)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

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

Use Firefox cookies for a members-only or age-restricted video:

```zsh
python src/main.py --cookies "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download a Kick live stream (tries yt-dlp, falls back to Playwright + ffmpeg automatically):

```zsh
python src/main.py "https://kick.com/username"
```

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

If the automated fallback also fails (e.g. Cloudflare blocks the headless browser), run `kick_live_downloader.py` directly with `--headful`:

```zsh
python src/kick_live_downloader.py --page "https://kick.com/username" --headful
```

### VOD replays — `kick_vod_downloader.py`

Downloads a VOD and its full chat history. Requires only the VOD URL — metadata, `channel_id`, and stream timestamps are resolved automatically.

```zsh
python src/kick_vod_downloader.py [OPTIONS] "URL"
```

`URL` must be a Kick VOD URL containing a UUID:

```text
https://kick.com/username/videos/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

| Option | Description |
| --- | --- |
| `--video-only` | Download video only, skip chat |
| `--chat-only` | Download chat only, skip video |
| `--chat-delay N` | Milliseconds between chat API requests (default: 300, min: 100) |

Examples:

```zsh
# Video + full chat (default)
python src/kick_vod_downloader.py "https://kick.com/username/videos/UUID"

# Chat only
python src/kick_vod_downloader.py --chat-only "https://kick.com/username/videos/UUID"

# Video only
python src/kick_vod_downloader.py --video-only "https://kick.com/username/videos/UUID"
```

Output is written to a new `kick_outputN/` folder:

| File | Contents |
| --- | --- |
| `metadata.json` | Raw VOD metadata from the Kick API |
| `<title>_chat.csv` | Chat messages (vod_offset, timestamp, username, user_id, message, type, badges, color, amount, message_id, metadata) |
| `<title>_chat.ndjson` | Raw chat messages, one JSON object per line |
| `<title>.mp4` | Downloaded video (unless `--chat-only`) |

The `vod_offset` column is formatted as `H:MM:SS` and gives the playback position in the downloaded video where each message appears — computed as `message_timestamp − vod_start_time`. Chat messages include emotes as `[emote:ID:name]` tokens. The `duration` field unit (seconds vs. milliseconds) is auto-detected. Increase `--chat-delay` if you encounter `429` rate-limit responses.

### Backfill: vod_offset for existing CSVs

If you have a `_chat.csv` downloaded before `vod_offset` was added, use `add_vod_offset.py` to retroactively add the column without re-downloading:

```zsh
# metadata.json auto-detected from the same folder as the CSV
python src/add_vod_offset.py kick_output1/title_chat.csv

# metadata.json in a different location
python src/add_vod_offset.py path/to/chat.csv path/to/metadata.json
```

Output is written to `<original_name>_with_offset.csv`. The original is not modified. If `vod_offset` already exists in the CSV it is dropped and recomputed, so the script is safe to run more than once.

### Filtering chat noise — `filter_chat.py`

Reduces a Kick VOD chat CSV to its substantive messages by removing four categories of noise:

| Filter | What it removes |
| --- | --- |
| Emote-only | Messages whose entire content is `[emote:ID:name]` tokens |
| Internal repetition | Messages where the same 5-word sequence appears 3+ times (copy-paste spam) |
| Per-user dedup | Identical messages from the same user within a rolling time window |
| Reaction flood | Short reaction messages (e.g. "L", "W", "lol") seen too many times in a short window |

```zsh
python src/filter_chat.py path/to/chat.csv
```

Output is written to `<input>_filtered.csv`. The original is not modified.

| Option | Default | Description |
| --- | --- | --- |
| `-o / --output` | `<input>_filtered.csv` | Output file path |
| `--user-dedup-window` | `120` | Seconds before a user can repeat the same message |
| `--reaction-window` | `30` | Sliding window (seconds) for reaction flood detection |
| `--reaction-max` | `5` | Max occurrences of a short reaction per window |
| `--reaction-len` | `15` | Messages at or under this character count are treated as reactions |
| `--no-emote-filter` | — | Keep emote-only messages |
| `--no-repeat-filter` | — | Keep internally repetitive messages |

## Dependencies

- `yt-dlp`: Download videos from YouTube and other sites.
- `click`: CLI framework.
- `pytz`: Timezone calculations.
- `browser-cookie3`: Read cookies from the browser for authenticated downloads.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Generated by AI

*Text generated by AI.*
