# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

> This script has not been tested. All versions below were written but never run against real data.

## [1.3.0] - 2026-03-09

### Added

- `--video FILE` argument to read `creation_time` metadata from the video file via ffprobe.
- `get_video_creation_time()` function that runs ffprobe and parses the `creation_time` tag from the format container.
- `choose_start_time()` function that displays both candidates (video `creation_time` and first chat message), shows the time difference between them, and recommends which is more likely to be the actual stream start:
  - Gap 0–600s: recommends video `creation_time` (consistent with a live download)
  - First chat earlier than video: recommends first chat (video was downloaded after stream ended)
  - Gap > 600s: recommends first chat as conservative estimate
- Interactive `[v/c/m(manual)]` prompt in `choose_start_time()` with the recommended option as default.
- `choose_start_time()` is now called in the fallback path whenever `--video` is provided or a first chat message is available, replacing the simpler yes/no prompt.

### Changed

- Fallback path (no `--start` and no `infojson`) now branches: if any candidate times are available, calls `choose_start_time()`; otherwise prints guidance and prompts manually.
- Guidance message for fully unknown start time updated to suggest `--video` as the best local fallback.

## [1.2.0] - 2026-03-09

### Added

- `get_first_message_time()` function that reads the first valid timestamp from the CSV.
- When no start time can be determined automatically, the script now prints a structured help message explaining the situation and available options (Wayback Machine, first chat approximation, ffprobe).
- Interactive prompt offering to use the first chat message time as a start time approximation, with a note that chat will appear slightly early and can be corrected with mpv-youtube-chat's time offset setting.

## [1.1.0] - 2026-03-09

### Added

- `parse_start_time()` function that accepts either a plain Unix timestamp (integer or float, as returned by `yt-dlp --print release_timestamp`) or a human-readable date string, enabling shell substitution like:
  
  ```bash
  python csv_to_livechat.py chat_log.csv --start "$(yt-dlp --print release_timestamp --skip-download -- VIDEO_ID)"
  ```

### Changed

- `--start` argument now uses `parse_start_time()` instead of `parse_eastern_timestamp()`.

## [1.0.0] - 2026-03-09

### Added

- Initial release.
- Converts `livechat.py` CSV output (Eastern Time wall-clock timestamps) to yt-dlp `.live_chat.json` format (video-relative millisecond offsets).
- `load_start_time_from_infojson()` reads `release_timestamp` or `timestamp` from a yt-dlp `.info.json` file.
- `parse_eastern_timestamp()` parses Eastern Time strings with or without explicit timezone suffix.
- `convert()` writes one JSON object per line matching yt-dlp's `replayChatItemAction` structure:
  - Regular messages → `liveChatTextMessageRenderer`
  - Superchats → `liveChatPaidMessageRenderer` with `purchaseAmountText`
- Skips the termination reason row appended by `livechat.py`.
- Warns on rows with negative video offsets (message before stream start) and skips them.
- `--start` flag for providing start time on the command line.
- `infojson` positional argument for automatic start time extraction.
- `--output` flag for custom output path; defaults to `<csv_stem>.live_chat.json`.
- Interactive `prompt_start_time()` fallback when no start time source is available.
