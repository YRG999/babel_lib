# YouTube Live Caption Fetcher

A Python tool that captures live transcriptions from YouTube live streams in real-time using local speech-to-text powered by Whisper.

## Features

- **Flexible URL Input**: Accept full YouTube URLs or video IDs
- **Local Transcription**: Uses mlx-whisper for on-device transcription (no API costs)
- **Apple Silicon Optimized**: Runs on GPU for fast transcription on M1/M2/M3 Macs
- **Real-Time Capture**: Transcribes audio in configurable chunks (default 10 seconds)
- **Multiple Model Sizes**: Choose accuracy vs. speed tradeoff
- **CSV Export**: Saves captions with timestamps to CSV
- **Automatic URL Refresh**: Handles stream URL expiration gracefully

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.8+
- ffmpeg
- yt-dlp
- Required Python packages (see setup)

## Setup

### 1. Install Homebrew dependencies

```bash
brew install ffmpeg pkg-config
```

### 2. Install Python packages

```bash
pip install mlx-whisper yt-dlp pytz
```

The `mlx-whisper` installation includes these dependencies:

- `mlx` and `mlx-metal` - Apple's ML framework
- `torch` - PyTorch
- `huggingface_hub` - Model downloads
- `tiktoken` - Tokenization
- `numba` and `llvmlite` - JIT compilation

### 3. First Run Model Download

On first run, the Whisper model will be downloaded from Hugging Face:

- `tiny`: ~75 MB
- `base`: ~140 MB
- `small`: ~460 MB
- `medium`: ~1.5 GB
- `large-v3`: ~3 GB

## Usage

Run the script:

```bash
python ytdownload/livecaptions.py
```

You'll be prompted for:

1. **Model size** - Accuracy vs. speed tradeoff (default: base)
2. **Language code** - e.g., "en" for English (default: en)
3. **Chunk duration** - Seconds between transcriptions (default: 10)
4. **YouTube URL or video ID** - accepts any of these formats:
   - Full URL: `https://www.youtube.com/watch?v=VIDEO_ID`
   - Short URL: `https://youtu.be/VIDEO_ID`
   - Live URL: `https://www.youtube.com/live/VIDEO_ID`
   - Just the ID: `VIDEO_ID`

### Example

```txt
Whisper model sizes (runs on Apple Silicon GPU):
  tiny   - Fastest, least accurate
  base   - Good balance [default]
  small  - Better accuracy
  medium - High accuracy
  large-v3 - Best accuracy (requires more memory)

Enter model size [base]:
Enter language code [en]:
Enter chunk duration in seconds [10]:
Enter YouTube URL or video ID: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Extracted video ID: dQw4w9WgXcQ
Model: base, Language: en, Chunk: 10s

Starting caption capture for video: dQw4w9WgXcQ
Output file: captions_dQw4w9WgXcQ_20260120_143052.csv
Model: base, Language: en
Chunk duration: 10s
Press Ctrl+C to stop

Loading Whisper model (this may take a moment on first run)...
Starting audio capture...
2026-01-20 14:30:52 EST: Hello everyone, welcome to the stream...
2026-01-20 14:31:02 EST: Today we're going to be talking about...
```

## Model Selection Guide

| Model | Speed | Accuracy | Memory | Best For |
| ------- | ------- | ---------- | -------- | ---------- |
| tiny | Fastest | Basic | ~1 GB | Quick testing, clear audio |
| base | Fast | Good | ~1 GB | General use, recommended |
| small | Medium | Better | ~2 GB | Important recordings |
| medium | Slower | High | ~5 GB | Professional use |
| large-v3 | Slowest | Best | ~10 GB | Maximum accuracy needed |

## Output Format

The script creates a CSV file with the following columns:

- **Timestamp (ET)**: Eastern Time timestamp of when the words were spoken
- **Start**: Start time within the chunk (seconds)
- **End**: End time within the chunk (seconds)
- **Text**: The transcribed text

Example output:

```csv
Timestamp (ET),Start,End,Text
2026-01-20 14:30:52 EST,0.00,3.42,"Hello everyone, welcome to the stream"
2026-01-20 14:30:55 EST,3.42,7.18,"Today we're going to be talking about"
```

The last row includes the termination reason (stream ended, user interrupt, etc.)

## How It Works

1. **Stream URL Acquisition**: Uses yt-dlp to get the live audio stream URL
2. **Audio Chunking**: ffmpeg captures audio in chunks (default 10 seconds)
3. **Transcription**: Each chunk is transcribed using mlx-whisper on the GPU
4. **Output**: Captions are printed to console and saved to CSV
5. **URL Refresh**: If the stream URL expires, it automatically fetches a new one

### Architecture

```txt
YouTube Live Stream
       │
       ▼
   yt-dlp (get stream URL)
       │
       ▼
   ffmpeg (capture audio chunks)
       │
       ▼
   mlx-whisper (transcribe on GPU)
       │
       ▼
   CSV file + console output
```

## Latency

The transcription delay is approximately:

- **Chunk duration** (default 10s) + **Transcription time** (~1-3s for base model)
- Total: ~11-15 seconds behind real-time

For lower latency, reduce chunk duration (e.g., 5 seconds), but this may affect accuracy for sentences that span chunk boundaries.

## Changelog

### [v1.0.0] - 2026-01-20

#### Initial Release

- Real-time live caption capture from YouTube streams
- Local transcription using mlx-whisper (Apple Silicon optimized)
- Support for multiple Whisper model sizes (tiny through large-v3)
- Configurable chunk duration for latency vs. accuracy tradeoff
- CSV export with timestamps
- Automatic stream URL refresh on expiration
- Same URL parsing as livechat.py for consistent UX

#### Core Features

- `LiveCaptionFetcher` class with threaded audio capture
- Uses ffmpeg for audio extraction (16kHz mono WAV)
- Queue-based processing for smooth transcription pipeline
- Graceful handling of stream end and user interrupts
- Dependency checking with helpful installation instructions

#### Dependencies installed

Homebrew:

- `pkg-config` - Required for building Python packages
- `ffmpeg` - Audio/video processing (likely already installed)

Python (via pip):

- `mlx-whisper` - Whisper implementation for Apple Silicon
- `mlx`, `mlx-metal` - Apple ML framework
- `torch` - PyTorch
- `huggingface_hub` - Model downloads
- `tiktoken` - Tokenization
- `numba`, `llvmlite` - JIT compilation
- `pytz` - Timezone handling (likely already installed from livechat.py)

## Error Handling

The script handles:

- Stream URL expiration (auto-refresh)
- Network errors and timeouts
- ffmpeg capture failures
- Transcription errors
- Keyboard interrupts (Ctrl+C)
- Stream ending naturally

All errors are logged, and the CSV file includes the termination reason.

## Tips

- Start with the `base` model - it's a good balance of speed and accuracy
- Use shorter chunk durations (5-7s) for lower latency if needed
- The script works best with clear audio; background music may affect accuracy
- You can run this alongside `livechat.py` to capture both chat and captions
- Press Ctrl+C to stop - the CSV is saved with all captured captions

## Troubleshooting

### "yt-dlp error" or no stream URL

- Verify the video ID is correct
- Ensure the stream is currently live
- Check your internet connection

### Transcription is slow

- Use a smaller model (tiny or base)
- Increase chunk duration to reduce processing overhead
- Ensure no other GPU-intensive tasks are running

### "mlx-whisper not found"

- Run: `pip install mlx-whisper`
- Ensure you're using the correct Python environment

### ffmpeg errors

- Verify ffmpeg is installed: `which ffmpeg`
- Try: `brew reinstall ffmpeg`

### Model download fails

- Check internet connection
- Try a smaller model first
- Hugging Face may have rate limits; try again later

## Comparison with livechat.py

| Feature | livechat.py | livecaptions.py |
| --------- | ------------- | ----------------- |
| Data source | YouTube API | Audio stream |
| Captures | Chat messages | Spoken words |
| API key needed | Yes | No |
| Quota limits | Yes (10k/day) | No |
| Works offline | No | After model download |
| Latency | ~5 seconds | ~10-15 seconds |

## License

Part of the babel_lib repository.
