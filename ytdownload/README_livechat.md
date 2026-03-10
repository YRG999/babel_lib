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

## Related Documentation

- [CHANGELOG_livechat.md](CHANGELOG_livechat.md) - Version history
- [README.md](README.md) - ytdownload toolkit overview
