# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-03-10

### Fixed

- Fixed capture continuing indefinitely after a live stream ends. When a stream ends, YouTube serves the VOD replay at the same URL, so ffmpeg kept successfully capturing chunks and `consecutive_failures` never incremented. Added `_is_stream_live()` (calls `yt-dlp --print is_live`) with two check points: (1) before refreshing a 403'd URL — if the stream has ended, stop immediately instead of getting a VOD URL; (2) every 10 chunks as a periodic liveness poll, stopping if the stream is no longer live.

## [1.3.0] - 2026-03-10

### Fixed

- Fixed consecutive word repetition hallucinations not caught by `compression_ratio` alone (e.g. "DON DON DON DON DON..." × 200). Root cause: for short segments, zlib compression overhead prevents the ratio from exceeding 2.4 even for highly repetitive text. Added a regex filter that discards any segment where the same word repeats 4 or more times consecutively (`\b(\w+)\b(?:\s+\1){3,}`).

## [1.2.0] - 2026-03-09

### Added

- Silence markers: after 5 minutes with no transcribed speech, writes a `[silence]` row to the CSV (with current timestamp, empty Start/End) and prints it to the console. Resets each time speech or a silence marker is written, so markers appear every 5 minutes throughout a long silent period.

### Fixed

- `_get_stream_url()` format selector changed from `bestaudio` to `bestaudio/best` so it falls back to the best combined format when no audio-only stream is available (common for live streams).
- Added `result: dict` type annotation to `_transcribe_chunk()` to resolve IDE false positive caused by `mlx_whisper` being imported lazily inside the function, which prevented the type checker from inferring the return type of `mlx_whisper.transcribe()`.
- Corrected all model names in `model_map` and fallback default to include the `-mlx` suffix required by mlx-community HuggingFace repos (e.g. `mlx-community/whisper-base-mlx` instead of `mlx-community/whisper-base`). Without the suffix, HuggingFace returns a 401 "Repository Not Found" error.
- Fixed timestamps appearing ~1 minute in the future. Caused by ffmpeg downloading audio from YouTube's CDN faster than real-time (buffered stream), so `chunk_index * chunk_duration` accumulated ahead of wall clock. Fixed by recording `chunk_capture_start = datetime.now()` immediately before each ffmpeg call and using that as the chunk timestamp, instead of computing from a fixed `start_time`.
- Fixed transcript duplication (repeated phrases like "I'm going to go to the next room" appearing 10+ times). Caused by Whisper hallucinating during silent/low-quality audio chunks. Fixed by: (1) setting `condition_on_previous_text=False` to stop Whisper feeding its previous output back as context, and (2) filtering out segments where `no_speech_prob >= 0.6` (Whisper's own confidence that no speech is present).
- Fixed additional hallucination patterns not caught by `no_speech_prob` alone (e.g. "to to to to to" × 50, "to depth to depth to depth" × 40), where Whisper was "confident" it heard speech but was pattern-matching noise. Added `compression_ratio < 2.4` filter per segment — repetitive text compresses extremely well, making this a reliable signal for hallucinated output.

## [1.1.0] - 2026-02-09

### Changed

- Renamed script from `livecaptions.py` to `captions.py` as part of a broader docs and error handling reorganization (commit `6853975`).

## [1.0.0] - 2026-01-20

### Added

- Initial release.
- Real-time live caption capture from YouTube streams using local speech-to-text.
- `LiveCaptionFetcher` class with threaded audio capture and queue-based transcription pipeline.
- Local transcription via mlx-whisper, optimized for Apple Silicon GPU (M1/M2/M3).
- Support for all Whisper model sizes: tiny, base, small, medium, large-v3.
- Configurable chunk duration (default 10s) for latency vs. accuracy tradeoff.
- ffmpeg audio extraction at 16kHz mono WAV for each chunk.
- CSV export with Eastern Time timestamps, segment start/end times, and transcribed text.
- Automatic stream URL refresh on expiration.
- Same URL parsing as `livechat.py` (full URLs and bare video IDs).
- Graceful handling of stream end and Ctrl+C interrupts.
- Termination reason written as final CSV row.
- Dependency checking with helpful installation instructions on missing packages.
