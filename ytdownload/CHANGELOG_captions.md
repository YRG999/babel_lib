# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
