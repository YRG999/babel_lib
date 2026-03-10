# csv_to_livechat

Converts a `livechat.py` CSV export to yt-dlp `.live_chat.json` format for replay in [mpv-youtube-chat](https://github.com/BanchouBoo/mpv-youtube-chat).

## Background

`livechat.py` saves chat to CSV with wall-clock Eastern Time timestamps. yt-dlp's `.live_chat.json` format uses millisecond offsets from the stream start (`videoOffsetTimeMsec`). This script bridges that gap.

### Version history summary

| Version | Feature added |
| --- | --- |
| 1.0.0 | Initial conversion: CSV → `.live_chat.json`, `--start`, `infojson` positional arg |
| 1.1.0 | `--start` accepts Unix timestamps (e.g. from `yt-dlp --print release_timestamp`) |
| 1.2.0 | Fallback guidance when start time is unknown; option to use first chat message |
| 1.3.0 | `--video` flag: reads `creation_time` via ffprobe and recommends best start time |

## Requirements

- Python 3.7+
- `pytz`, `python-dateutil` (already required by `livechat.py`)
- `ffmpeg` / `ffprobe` — optional, needed for `--video` creation_time reading

## Usage

```bash
python ytdownload/csv_to_livechat.py CHAT_LOG.csv [INFO.json] [options]
```

| Argument | Description |
| --- | --- |
| `CHAT_LOG.csv` | CSV file produced by `livechat.py` |
| `INFO.json` | _(optional)_ yt-dlp `.info.json` — reads `release_timestamp` for stream start |
| `--start TIME` | Stream start time as a date string or Unix timestamp |
| `--video FILE` | Video file path — reads `creation_time` via ffprobe and compares to first chat message |
| `--output FILE` | Output path (default: `<csv_stem>.live_chat.json`) |

### Examples

```bash
# Auto-detect from info.json
python csv_to_livechat.py chat_log_ABC123.csv "Stream Title [ABC123].info.json"

# Fetch start time from yt-dlp without re-downloading
python csv_to_livechat.py chat_log_ABC123.csv --start "$(yt-dlp --print release_timestamp --skip-download -- ABC123)"

# Provide start time as a date string
python csv_to_livechat.py chat_log_ABC123.csv --start "2024-01-15 20:00:00 EST"

# Compare video creation_time vs first chat message (interactive)
python csv_to_livechat.py chat_log_ABC123.csv --video stream.mp4

# No arguments — interactive prompts guide you through start time selection
python csv_to_livechat.py chat_log_ABC123.csv
```

## Start Time Detection

The script tries to determine the stream start time in this order:

1. `--start` flag (Unix timestamp or date string)
2. `INFO.json` positional argument (`release_timestamp` or `timestamp` field)
3. Interactive selection via `--video` (ffprobe `creation_time` vs first chat message)
4. Interactive prompt to enter manually

If the video has been deleted from YouTube and no `.info.json` exists, the `--video` flag is the best fallback. The script compares the video file's `creation_time` against the first chat message timestamp and recommends which to use:

- **Gap 0–600s**: video `creation_time` likely reflects the live download start — recommended
- **First chat is earlier than video**: video was downloaded after the stream ended — first chat recommended
- **Gap > 600s**: suspiciously large — first chat recommended as conservative estimate

## Output

A `.live_chat.json` file (one JSON object per line) matching yt-dlp's replay format. Superchats are written as `liveChatPaidMessageRenderer`; all other message types as `liveChatTextMessageRenderer`.

Default output name: `<csv_stem>.live_chat.json` in the same directory as the CSV.

## Using the Output with mpv

1. Install [mpv-youtube-chat](https://github.com/BanchouBoo/mpv-youtube-chat) into your mpv scripts folder
2. Rename the output so the stem matches the video filename:
   - Video: `my_stream.mp4`
   - Chat: `my_stream.live_chat.json`
3. Play the video in mpv — chat loads automatically

If the chat appears out of sync, use mpv-youtube-chat's configurable time offset to nudge it.

## Related Documentation

- [README_livechat.md](README_livechat.md) — livechat.py usage and CSV output format
- [CHANGELOG_csv_to_livechat.md](CHANGELOG_csv_to_livechat.md) — version history
- [README.md](README.md) — ytdownload toolkit overview
