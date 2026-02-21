# YouTube Live Chat Fetcher

A Python tool that captures YouTube live chat messages in real-time and automatically downloads the live stream video simultaneously.

## Features

- **Flexible URL Input**: Accept full YouTube URLs or video IDs
- **Automatic Video Download**: Opens a new terminal window running yt-dlp to download the live stream
- **Live Chat Capture**: Fetches and logs all chat messages, Super Chats, Super Stickers, and new sponsors
- **Quota Management**: Intelligent API quota tracking to avoid exceeding daily limits
- **Dynamic Polling**: Adjusts polling intervals based on API quota and expected stream duration
- **CSV Export**: Saves chat logs with timestamps, authors, messages, and Super Chat amounts
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Requirements

- Python 3.7+
- YouTube Data API v3 key
- yt-dlp installed and available in PATH
- Required Python packages (see setup)

## Setup

1. **Install required packages:**

   ```zsh
   pip install google-api-python-client python-dotenv pytz python-dateutil
   ```

2. **Install yt-dlp:**

   ```zsh
   pip install yt-dlp
   # or
   brew install yt-dlp  # macOS
   ```

3. **Configure API Key:**
   Create a `.env` file in the project root with your YouTube API key:

   ```zsh
   YOUTUBE_API_KEY=your_api_key_here
   ```

   To get an API key:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project
   - Enable YouTube Data API v3
   - Create credentials (API Key)

## Usage

Run the script:

```zsh
python ytdownload/livechat.py
```

You'll be prompted for:

1. **Expected stream duration** (in hours) - helps with quota management
2. **YouTube URL or video ID** - accepts any of these formats:
   - Full URL: `https://www.youtube.com/watch?v=VIDEO_ID`
   - Short URL: `https://youtu.be/VIDEO_ID`
   - Live URL: `https://www.youtube.com/live/VIDEO_ID`
   - Just the ID: `VIDEO_ID`

### Example

```txt
Enter expected live stream duration in hours (e.g., 4): 3
Enter YouTube URL or video ID: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Extracted video ID: dQw4w9WgXcQ
Opening new terminal window to download live stream...

Starting live chat capture...
```

The script will:

1. Extract the video ID from your input
2. Open a new terminal window that runs `yt-dlp --live-from-start -- VIDEO_ID`
3. Start capturing live chat in the current terminal
4. Save all messages to a CSV file: `chat_log_VIDEO_ID_TIMESTAMP.csv`

## Changelog

### [v16.0.2] - 2026-01-20

**Added** - Optional video download toggle

Added a prompt to skip video downloading when restarting the live chat capture. Useful when the chat capture stops mid-stream but the video is still downloading in another terminal.

**Changes:**

- New prompt after entering video ID: `Download video as well? (y/n) [y]:`
- Press Enter or `y` to download video and capture chat (existing behavior)
- Type `n` to skip video download and only capture live chat

### [v16.0.1] - 2026-01-20

**Fixed** - Virtual environment activation in new terminal windows

When running the script from within a virtual environment, the new terminal window now automatically activates the same virtual environment before executing yt-dlp. This ensures that yt-dlp and all dependencies are accessible in the spawned terminal.

**Changes:**

- Added `get_venv_activation_command()` function that:
  - Detects if running in a virtual environment using `VIRTUAL_ENV` environment variable
  - Falls back to comparing `sys.prefix` vs `sys.base_prefix` for alternative detection
  - Locates the correct activation script path for the current platform
  - Returns `None` if not running in a virtual environment

- Updated `open_terminal_with_ytdlp()` function to:
  - Detect virtual environment before building commands
  - Prepend activation command to yt-dlp execution
  - Platform-specific implementations:
    - **macOS/Linux**: `source "/path/to/venv/bin/activate" && yt-dlp ...`
    - **Windows**: `"path\to\venv\Scripts\activate.bat" && yt-dlp ...`
  - Log virtual environment activation for debugging

**Benefits:**

- No more "command not found" errors when yt-dlp is installed in a virtual environment
- Consistent environment between chat capture and video download processes
- Works seamlessly with Poetry, venv, virtualenv, and conda environments

### [v16.0.0] - 2026-01-20

**Added** - URL parsing, automatic stream download, and streamlined workflow

This major release changes the user interface to accept full YouTube URLs instead of just video IDs, and introduces automatic live stream downloading in a separate terminal window.

**Breaking Changes:**

- Changed input prompt from "Enter video ID:" to "Enter YouTube URL or video ID:"
- The script now accepts full YouTube URLs (backward compatible with video IDs)

**New Features:**

- **URL Parsing Enhancement:**
  - Added `extract_video_id()` function to accept full YouTube URLs
  - Supports multiple URL formats (standard, short, embed, live)
  - Backward compatible with direct video ID input

- **Automatic Stream Download:**
  - Added `open_terminal_with_ytdlp()` function
  - Automatically detects OS (macOS, Linux, Windows)
  - Opens new terminal window with yt-dlp command
  - No manual intervention needed to start video download

- **Streamlined Workflow:**
  - Removed manual prompt to start chat capture
  - Both processes (video download + chat capture) start automatically
  - Improved user experience with clearer status messages

### [v15.0.0] - Base Version

**Core Features:**

- YouTube live chat capture with real-time logging
- Quota management system with `QuotaManager` class
- Support for all chat message types (text, Super Chats, Super Stickers, sponsors)
- CSV export with Eastern Time timestamps
- Dynamic polling interval calculation
- Cross-session quota tracking
- Error handling for API limits and stream ending

## Output Format

The script creates a CSV file with the following columns:

- **Timestamp (ET)**: Eastern Time timestamp of the message
- **Author**: Display name of the message author
- **Message**: The chat message content
- **Message Type**: Type of event (textMessageEvent, superChatEvent, etc.)
- **SuperChat Amount**: Amount if it's a Super Chat or Super Sticker

The last row includes the termination reason (chat ended, quota exceeded, user interrupt, etc.)

## Quota Management

The script includes intelligent quota management:

- Tracks API usage across multiple sessions
- Calculates optimal polling intervals
- Prevents quota exhaustion mid-stream
- Stores quota data in `.youtube_quota.json`

Daily quota limit: 10,000 units (configurable)

- `videos.list` call: 1 unit
- `liveChatMessages.list` call: 5 units

## Chat Message Types

The script captures and logs:

- **Text Messages**: Regular chat messages
- **Super Chats**: Paid messages with amount
- **Super Stickers**: Paid stickers with amount
- **New Sponsors**: Channel membership events
- **Other Events**: Any other chat events

## Platform-Specific Terminal Support

- **macOS**: Uses AppleScript to open Terminal.app
- **Linux**: Tries gnome-terminal, konsole, then xterm
- **Windows**: Opens Command Prompt (cmd)

## Error Handling

The script handles:

- API quota limits and rate limiting
- Live chat ending naturally
- Network errors and HTTP errors
- Keyboard interrupts (Ctrl+C)
- Invalid video IDs or non-live streams

All errors are logged, and the CSV file includes the termination reason.

## Tips

- Start the script shortly after the stream begins for complete coverage
- Set expected duration accurately for better quota management
- The yt-dlp download will capture from the start of the live stream
- Chat logs are flushed to disk every 5 minutes to prevent data loss
- You can safely interrupt with Ctrl+C - progress is saved

## Troubleshooting

### "Video not found or not a live stream"

- Verify the video ID is correct
- Ensure the stream is currently live
- Check that live chat is enabled for the stream

### "API quota exceeded"

- Wait until the next day (resets at midnight Pacific Time)
- Reduce polling frequency by increasing expected duration
- Use multiple API keys if needed

### Terminal doesn't open automatically

- Verify yt-dlp is installed: `which yt-dlp`
- Check terminal emulator is available on your system
- Manually run the displayed yt-dlp command if needed

## License

Part of the babel_lib repository.
