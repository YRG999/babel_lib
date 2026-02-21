# ytdownload

YouTube live content capture and analysis toolkit. Designed for real-time streaming with tools for live chat capture, speech-to-text transcription, video downloading, and data analysis.

## Features

- **Live Chat Capture** - Real-time YouTube live chat message collection via YouTube Data API v3
- **Live Transcription** - Speech-to-text transcription of live streams using mlx-whisper (Apple Silicon GPU-optimized)
- **Video Downloading** - Download videos, comments, transcripts, and metadata
- **Data Analysis** - Process and analyze captured chat data with statistics
- **API Quota Management** - Intelligent tracking of YouTube API usage with multi-process safety

## Files

### Core Tools

| File                     | Size   | Description                                        |
| ------------------------ | ------ | -------------------------------------------------- |
| `livechat.py`            | 22 KB  | Main live chat capture tool with quota management  |
| `captions.py`            | 15 KB  | Real-time transcription using mlx-whisper          |
| `download.py`            | 6.6 KB | Video/comment/transcript downloader                |
| `youtube_downloader6.py` | 6.9 KB | Alternative downloader with Firefox cookie support |
| `analyze.py`             | 6 KB   | Live chat statistical analysis                     |
| `comments.py`            | 4.5 KB | Comment download utility                           |

### Utilities

| File                   | Description                               |
| ---------------------- | ----------------------------------------- |
| `extract_functions.py` | Shared helpers for emoji/text extraction  |
| `firefox_cookies.py`   | Browser cookie handler for authentication |
| `report_formats.py`    | List available video formats              |
| `merge_parts.py`       | Merge yt-dlp .part files using ffmpeg     |
| `count_livechat.py`    | Simple message counter                    |

### Documentation

| File                     | Description                        |
| ------------------------ | ---------------------------------- |
| `README_livechat.md`     | Detailed livechat.py documentation |
| `README_livecaptions.md` | Detailed captions.py documentation |

### Configuration

| File                  | Description                       |
| --------------------- | --------------------------------- |
| `.youtube_quota.json` | API quota tracking (auto-managed) |
| `.env`                | Environment variables (API keys)  |

## Installation

### Prerequisites

**External tools:**

```bash
# yt-dlp - YouTube downloading engine
brew install yt-dlp  # or pip install yt-dlp

# ffmpeg - Audio/video processing
brew install ffmpeg
```

**Python packages:**

```bash
pip install google-api-python-client  # YouTube Data API v3
pip install python-dotenv             # Environment variable management
pip install pytz                      # Timezone handling
pip install python-dateutil           # Date parsing
pip install emoji                     # Emoji detection
pip install pandas                    # Data analysis
pip install mlx-whisper               # Apple Silicon transcription (macOS only)
```

### Configuration

1. Create a `.env` file in the ytdownload folder:

   ```bash
   YOUTUBE_API_KEY=your_api_key_here
   ```

   > [Uses 1Password to store API credentials](https://developer.1password.com/docs/cli/use-cases#secrets)

2. Get a YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## Usage

All main scripts have interactive `main()` functions that prompt for input. They accept both full YouTube URLs and video IDs.

### Live Chat Capture

```bash
python livechat.py
```

Captures live chat messages in real-time. Automatically:

- Opens a new terminal window to download the video via yt-dlp
- Tracks API quota usage
- Exports to CSV with Eastern Time timestamps

**Output:** `{video_id}_livechat_{termination_reason}.csv`

**Columns:** Timestamp (ET), Author, Message, Message Type, SuperChat Amount

### Live Transcription

```bash
python captions.py
```

Real-time speech-to-text transcription using mlx-whisper (requires Apple Silicon Mac).

**Options:**

- Whisper model sizes: tiny, base, small, medium, large-v3
- Configurable chunk duration (default 10 seconds)

**Output:** `{video_id}_livecaptions_{termination_reason}.csv`

**Columns:** Timestamp (ET), Start, End, Text

### Video Download

```bash
python download.py
```

Downloads video, audio, subtitles, and live chat. Supports "livechat_only" mode.

### Chat Analysis

```bash
python analyze.py
```

Generates statistical analysis of captured chat data:

- Superchat counts and totals by currency
- Message counts per author
- Stream duration calculations
- Markdown summary tables

**Output:** Markdown file with statistics

### Comment Download

```bash
python comments.py
```

Downloads all comments from a video to CSV.

**Output:** CSV with Comment ID, Author, Text, Timestamp, Eastern Time, Likes

## Architecture

### Live Chat Capture Workflow

```text
YouTube Live Stream
        ↓
Extract Video ID (from URL or direct ID)
        ↓
YouTube Data API v3 (with quota tracking)
        ↓
Chat messages (with timestamps)
        ↓
Convert to Eastern Time
        ↓
Handle message types (text, superchat, stickers, sponsors)
        ↓
CSV export with termination reason
```

### Live Caption Workflow

```text
YouTube Live Stream
        ↓
yt-dlp → Audio stream URL
        ↓
ffmpeg → Audio chunks (16kHz mono WAV)
        ↓
mlx-whisper → Transcription (GPU accelerated)
        ↓
Calculate segment timestamps
        ↓
CSV export with termination reason
```

## API Quota Management

YouTube Data API v3 has a daily quota limit of **10,000 units**.

### Quota Costs

| API Call                | Cost    |
| ----------------------- | ------- |
| `videos.list`           | 1 unit  |
| `liveChatMessages.list` | 5 units |

### Features

- **File-based tracking** - Quota persists in `.youtube_quota.json`
- **File locking** - Safe for multiple concurrent processes
- **Auto-reset** - Quota resets daily at midnight Pacific Time
- **Dynamic polling** - Adjusts poll rate based on remaining quota and expected stream duration

## Key Classes

### livechat.py

| Class                    | Purpose                                                 |
| ------------------------ | ------------------------------------------------------- |
| `QuotaManager`           | Manages daily API quota with file-based locking         |
| `YouTubeLiveChatFetcher` | Fetches live chat messages and handles API interactions |

**Custom Exceptions:**

- `LiveChatEnded` - Stream ended normally
- `QuotaExceeded` - Daily quota limit reached
- `UnrecoverableAPIError` - Fatal API error

### captions.py

| Class                | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `LiveCaptionFetcher` | Manages audio capture and transcription pipeline |

Uses threaded architecture: audio capture in background thread, transcription in main thread with queue-based processing.

## Code Patterns

- **Type hints** - Full annotations throughout (`List[str]`, `Dict[str, Any]`, `Optional[...]`)
- **Eastern Time** - All timestamp outputs use US/Eastern timezone
- **CSV exports** - Primary output format for all data
- **Context managers** - File locking with `@contextmanager`
- **Logging** - Structured logging to files and console
- **Threading** - Multi-threaded processing for audio pipelines
- **Cross-platform** - OS detection for terminal/shell integration (macOS, Linux, Windows)
- **Graceful degradation** - Handles API limits, network errors, stream endings

## Configuration Reference

| Setting                | Default      | Description                  |
| ---------------------- | ------------ | ---------------------------- |
| Daily quota limit      | 10,000 units | YouTube API limit            |
| Chat flush interval    | 300 seconds  | How often to write to CSV    |
| Caption chunk duration | 10 seconds   | Audio segment length         |
| Whisper model          | base         | Transcription model size     |
| Audio settings         | 16kHz mono   | WAV format for transcription |
| Timezone               | US/Eastern   | All timestamp outputs        |

## Output Examples

### Live Chat CSV

```csv
Timestamp (ET),Author,Message,Message Type,SuperChat Amount
2024-01-15 14:30:22,username1,Hello everyone!,text_message,
2024-01-15 14:30:45,username2,Great stream!,super_chat,$5.00
```

### Live Captions CSV

```csv
Timestamp (ET),Start,End,Text
2024-01-15 14:30:22,0.0,10.0,Welcome back everyone to today's stream
2024-01-15 14:30:32,10.0,20.0,We're going to be talking about...
```

### Analysis Output (Markdown)

```markdown
## Stream Statistics

- Total messages: 1,234
- Unique authors: 456
- Stream duration: 2h 30m

## Superchat Summary

| Currency | Count | Total |
|----------|-------|-------|
| USD | 25 | $150.00 |
| EUR | 5 | €45.00 |
```

## Platform Notes

- **macOS (Apple Silicon)** - Full support including mlx-whisper GPU acceleration
- **macOS (Intel)** - Supported, but captions.py requires alternative whisper implementation
- **Linux** - Supported, captions.py requires alternative whisper implementation
- **Windows** - Supported with platform-specific terminal launching

## Troubleshooting

### Quota Exceeded

If you hit the daily quota limit:

- Wait until midnight Pacific Time for reset
- Or use a different API key

### Live Stream Not Found

- Ensure the stream is currently live (not scheduled or ended)
- Check that the video ID or URL is correct

### mlx-whisper Errors

- Requires Apple Silicon Mac (M1/M2/M3/M4)
- Install with: `pip install mlx-whisper`

### Authentication Errors

For age-restricted or member-only content:

- Use Firefox cookies via `firefox_cookies.py`
- Ensure you're logged into YouTube in Firefox

## Related Documentation

- [README_livechat.md](README_livechat.md) - Detailed livechat.py documentation
- [README_livecaptions.md](README_livecaptions.md) - Detailed captions.py documentation
