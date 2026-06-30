# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-30

### Added

- Initial collection of stand-alone analysis scripts moved into `youtube-study/analysis/`:
  - `analyze.py` (formerly `ytdownload/analyze.py`) — YouTube live chat CSV analysis: superchat stats, author rankings, stream duration, markdown summary output.
  - `infojson2csv.py` (formerly `ytdownload/infojson2csv.py`, v1.1.0) — Batch parse yt-dlp `.info.json` files into a single CSV.
  - `filter_chat.py` (formerly `youtube-downloader-app/src/filter_chat.py`) — Kick chat CSV noise filter: emote-only, internal repetition, per-user dedup, reaction floods.
  - `add_vod_offset.py` (formerly `youtube-downloader-app/src/add_vod_offset.py`) — Backfill `vod_offset` (H:MM:SS) column into Kick VOD chat CSVs.
  - `timestamp_converter.py` (formerly `youtube-downloader-app/src/timestamp_converter.py`) — Interactive EST ↔ Unix epoch timestamp converter.
