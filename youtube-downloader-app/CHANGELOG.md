# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2026-03-27

### Fixed

- `vtt_to_text.py`: function never returned the output path — `main.py` always fell back to recomputing it. Now returns the path correctly.
- `comments.py`: CSV progress logging used `percentage % 10 == 0`, which never triggers for non-round comment counts. Replaced with a threshold tracker.

### Changed

- `livechat_to_csv.py`: extracted `_format_ts`, `_extract_runs_text`, and `_extract_role` helpers to eliminate duplicated logic across renderer types. Added missing `role` key to membership, system, and sticker row dicts for consistency.
- `livechat_to_csv.py`: removed dead "Moderation messages (deleted)" block — it checked `liveChatTextMessageRenderer` after that renderer was already matched and returned earlier.
- `main.py`: collapsed redundant three-branch `if transcript_only / elif metadata_only / else` into `convert_transcripts()` followed by `if not transcript_only`.
- `comments.py`: removed stale filepath comment and commented-out dead function.
- `extract_comments.py`: removed stale editor tip comment.

### Removed

- `utils.py`: unused — `convert_to_eastern` superseded by `extract_comments.py`, `get_user_input` superseded by the click CLI.
- `extract_functions.py`: unused — `extract_text_and_emoji` and `extract_timestamp` superseded by helpers in `livechat_to_csv.py`.

## [2.1.1] - 2026-03-26

### Added

- `kick_vod_downloader.py`: chat CSV now includes a `vod_offset` column (first column, formatted `H:MM:SS`) giving the playback position in the downloaded video for each message, computed as `message_timestamp − vod_start_time`.
- `add_vod_offset.py`: standalone backfill script to retroactively add the `vod_offset` column to existing Kick VOD chat CSVs downloaded before this feature was added. Reads `start_time` from `metadata.json`, computes `H:MM:SS` offset per row, writes to `<name>_with_offset.csv` (original untouched). Handles missing metadata, already-present `vod_offset`, unparseable timestamps, and logs progress every 50,000 rows.

## [2.1.0] - 2026-03-26

### Added

- `kick_vod_downloader.py`: downloads Kick.com VOD replays and full chat history (CSV + NDJSON).
  - VOD metadata (`channel_id`, `start_time`, `duration`) fetched automatically from `kick.com/api/v1/video/{uuid}`.
  - Chat fetched via time-windowed polling of `web.kick.com/api/v1/chat/{channel_id}/history` in 5-second windows.
  - Message deduplication by ID and chronological sort before output.
  - Chat exported to CSV (`timestamp`, `username`, `user_id`, `message`, `type`, `badges`, `color`, `amount`, `message_id`, `metadata`) and raw NDJSON.
  - `metadata.json` saved alongside outputs.
  - `--video-only`, `--chat-only`, and `--chat-delay` flags.
  - Auto-detection of Kick's `duration` field unit (seconds vs. milliseconds).
  - Retry logic with exponential backoff (up to 5 attempts) and `429` rate-limit handling.
  - Output written to a new `kick_outputN/` folder.
- `main.py`: Kick live stream support — detects `kick.com/username` URLs, tries yt-dlp first, and automatically falls back to `kick_live_downloader` (Playwright + ffmpeg) on failure.
- `kick_live_downloader.py`: m3u8 auto-detection via Playwright network interception — `--m3u8` is now optional; the URL is captured from the player's network traffic when omitted.
- `kick_live_downloader.download_kick_live()`: callable function so `main.py` can invoke the fallback directly without a subprocess.

### Changed

- `kick_downloader.py` renamed to `kick_live_downloader.py` to distinguish it from the new VOD downloader.

## [2.0.0] - 2026-03-04

### Added

- `--metadata-only` flag: skip video download and fetch subtitles, live chat, description, and info JSON, then convert transcripts and live chat automatically.
- `--transcript-only` flag: download subtitles only and convert to deduplicated text.
- `--comments` flag: opt-in comment downloading and CSV extraction (previously an interactive prompt).
- `--cookies` flag: opt-in Firefox cookie support (previously an interactive prompt).
- `click` added as a dependency.

### Changed

- `main.py` rewritten as a `click` CLI; URL is now a positional argument instead of an interactive prompt.
- Comments are not downloaded by default (previously prompted each run).
- `downloader.py` `comments_only` parameter replaced by `metadata_only` and `transcript_only`.
- `metadata_only` mode fetches subtitles and live chat in addition to info JSON; `transcript_only` mode fetches English subtitles only (no live chat).

### Removed

- Interactive prompt-based interface in `main.py`.
- `comments_only` parameter from `YouTubeDownloader`.

## [1.3.0] - 2026-02-09

### Added

- `timestamp_converter.py`: EST/epoch timestamp converter utility.
- FFmpeg availability check in `downloader.py` — warns the user if FFmpeg is not installed when downloading video.

## [1.2.3] - 2025-12-19

### Added

- `livechat_to_csv.py`: support for vertical livestream gift rows in live chat export.

## [1.2.2] - 2025-11-29

### Changed

- `downloader.py`: added `remote_components: ejs:npm` option to improve compatibility with yt-dlp.

## [1.2.1] - 2025-11-26

### Changed

- `downloader.py`: relaxed video format preference to `bv*+ba/best` for broader compatibility.

## [1.2.0] - 2025-11-15

### Added

- `firefox_cookie_export.py`: utility to export Firefox cookies for use with yt-dlp.
- `kick_downloader.py`: downloader support for Kick.com streams.
- `livechat_to_csv.py`: expanded live chat event type handling.

## [1.1.1] - 2025-07-30

### Changed

- `remove_dupe_lines.py`: simplified deduplication logic.
- `main.py`: minor tweak to deduplication call.

## [1.1.0] - 2025-07-01

### Added

- `remove_dupe_lines.py`: deduplicate converted transcript lines.
- `livechat_to_csv.py`: expanded CSV output with additional live chat event types.
- `extract_comments.py`: handle edge cases in comment extraction.

### Changed

- `main.py`: orchestrate VTT conversion, live chat CSV export, and comment extraction after download.

## [1.0.0] - 2025-06-20

### Added

- Initial release generated with GitHub Copilot.
- `downloader.py`: yt-dlp-based video downloader with cookie and comment support.
- `main.py`: interactive prompt interface for URL, cookies, and comment options.
- `extract_comments.py`: extract comments from `.info.json` to CSV.
- `livechat_to_csv.py`: convert live chat NDJSON files to CSV.
- `vtt_to_text.py`: convert VTT subtitle files to plain text.
- `comments.py`, `utils.py`, `extract_functions.py`: supporting utilities (latter two removed in 2.1.2).
- `requirements.txt` with initial dependencies.

## Generated by AI

*Text generated by AI.*
