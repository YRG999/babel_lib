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
python ytdownload/captions.py
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

- **Timestamp (ET)**: Eastern Time wall-clock timestamp of when the words were spoken. This is the primary time reference — computed as the moment the audio chunk began capturing plus the segment's Start offset.
- **Start**: Start time of the segment within its audio chunk (seconds). Not a wall-clock time — resets to 0 at the beginning of each chunk.
- **End**: End time of the segment within its audio chunk (seconds). Same frame of reference as Start.
- **Text**: The transcribed text. `[silence]` rows have an empty Start and End and indicate that no speech was detected for 5 or more consecutive minutes.

Example output:

```csv
Timestamp (ET),Start,End,Text
2026-01-20 14:30:52 EST,0.00,3.42,"Hello everyone, welcome to the stream"
2026-01-20 14:30:55 EST,3.42,7.18,"Today we're going to be talking about"
```

In this example, both rows come from the same 10-second audio chunk:

- `Start: 0.00, End: 3.42` — spoken in the first 3.4 seconds of the chunk
- `Start: 3.42, End: 7.18` — spoken from 3.4s to 7.2s into the chunk
- The **Timestamp** for each row is `chunk_capture_start + Start`, so it reflects the actual wall-clock time those words were spoken

Each transcribed segment is written to the CSV immediately. The file buffer is flushed to disk every 60 seconds, so in the worst case you could lose up to 60 seconds of captions if the process is killed ungracefully. A clean exit (Ctrl+C or stream ending naturally) always flushes before closing.

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

## Cost & Runtime

**There are no API costs.** Everything runs locally on your Mac:

- `yt-dlp` fetches a stream URL from YouTube for free
- `ffmpeg` downloads audio chunks directly from that URL
- `mlx-whisper` transcribes on your Apple Silicon GPU — no cloud, no tokens, no billing

The only resources consumed are electricity and GPU time on your own machine.

**It can run for hours.** The script is designed to run for the full duration of a live stream. The main limits are:

- **Stream URL expiration** — YouTube stream URLs expire periodically; the script detects the 403 error and automatically fetches a new URL
- **Disk space** — audio chunks are written to a temp directory and deleted immediately after transcription, so disk usage stays flat; only the CSV grows
- **GPU memory** — the Whisper model stays loaded the whole time (~500 MB for `base`); no other memory accumulates

The only things that stop it are Ctrl+C, the stream ending naturally, or too many consecutive ffmpeg failures.

## Latency

The transcription delay is approximately:

- **Chunk duration** (default 10s) + **Transcription time** (~1-3s for base model)
- Total: ~11-15 seconds behind real-time

For lower latency, reduce chunk duration (e.g., 5 seconds), but this may affect accuracy for sentences that span chunk boundaries.

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

| Feature | livechat.py | captions.py |
| --------- | ------------- | ----------------- |
| Data source | YouTube API | Audio stream |
| Captures | Chat messages | Spoken words |
| API key needed | Yes | No |
| Quota limits | Yes (10k/day) | No |
| Works offline | No | After model download |
| Latency | ~5 seconds | ~10-15 seconds |

## License

Part of the babel_lib repository.

## Related Documentation

- [CHANGELOG_captions.md](CHANGELOG_captions.md) - Version history
- [README.md](README.md) - ytdownload toolkit overview
