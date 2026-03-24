# ytdownload Module

YouTube live content capture and analysis tools focused on real-time streaming.

## Purpose

This module provides tools for:

- **Live chat capture** - Real-time YouTube live chat collection via YouTube Data API v3
- **Live transcription** - Speech-to-text of live streams using mlx-whisper (run separately from live chat)
- **Video downloading** - Download videos, comments, and metadata via yt-dlp
- **Data analysis** - Statistical analysis of captured chat data

## Key Files

| File | Purpose |
| --- | --- |
| `livechat.py` | Main live chat fetcher with API quota management |
| `captions.py` | Real-time transcription using mlx-whisper (Apple Silicon optimized) — independent of `livechat.py` |
| `csv_to_livechat.py` | Convert `livechat.py` CSV to yt-dlp `.live_chat.json` for mpv replay (untested) |
| `download.py` | Video/transcript/chat downloader |
| `analyze.py` | Chat statistics and superchat analysis |
| `comments.py` | Download video comments to CSV |
| `infojson2csv.py` | Convert yt-dlp `.info.json` files to CSV |
| `extract_functions.py` | Shared helpers for emoji/text extraction |

## Dependencies

**External tools:**

- `yt-dlp` - YouTube downloading
- `ffmpeg` - Audio/video processing (also used by `captions.py` for chunked audio capture)

**Python packages:**

- `google-api-python-client` - YouTube Data API v3
- `python-dotenv` - Environment variables (.env)
- `pytz` - Timezone handling
- `mlx-whisper` - Apple Silicon GPU transcription (required by `captions.py` only)
- `emoji` - Emoji detection
- `pandas` - Data analysis

## Configuration

- **API Key:** Stored in `.env` file as `YOUTUBE_API_KEY`
- **Quota tracking:** `.youtube_quota.json` (auto-managed, file-locked for multi-process safety)
- **Daily quota limit:** 10,000 units (YouTube API limit)
- **Quota costs:** 1 unit per `videos.list`, 5 units per `liveChatMessages.list`

## Code Conventions

- **Type hints** throughout (`List[str]`, `Dict[str, Any]`, `Optional[...]`)
- **Eastern Time (US/Eastern)** for all timestamp outputs
- **CSV exports** as primary output format
- **Custom exceptions** for API errors: `LiveChatEnded`, `QuotaExceeded`, `UnrecoverableAPIError`
- **Logging** to both console and files
- **Context managers** for file locking
- **Threading** for audio capture pipelines

## Important Context

- `livechat.py` and `captions.py` are independent tools — run them in separate terminals simultaneously to capture both chat and speech
- `captions.py` requires Apple Silicon Mac for mlx-whisper GPU acceleration
- `captions.py` hallucination filters: `no_speech_prob < 0.6`, `compression_ratio < 2.4`, and a regex check for words repeating 4+ times consecutively
- All tools accept either full YouTube URLs or video IDs
- `livechat.py` auto-opens a terminal to download the video via yt-dlp simultaneously
- Output filenames include video ID and termination reason
- `csv_to_livechat.py` has not been tested — header comment and `[Unreleased]` changelog section mark it as such

## Running

All main scripts have interactive `main()` functions that prompt for input:

```bash
python livechat.py   # Prompts for video URL/ID
python captions.py   # Prompts for video URL/ID (Apple Silicon only)
python analyze.py    # Prompts for CSV file path
```
