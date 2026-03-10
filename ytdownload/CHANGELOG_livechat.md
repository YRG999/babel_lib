# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions 4, 6, 7, 10, and 14 were committed to this repository before `livechat.py` existed; their dates are git commit dates. Versions 1–3, 5, 8a, 8b, 9, 11–13 were developed outside the repository; their dates are file modification timestamps.

---

## [3.3.0] - 2026-02-09

> Historic version: v16.2

### Added

- `ensure_1password_signin()` function that checks authentication status via `op account get` and automatically invokes `op signin` if needed, with a 5-minute interactive timeout.
- `get_youtube_api_key()` now calls `ensure_1password_signin()` before attempting to resolve any `op://` secret reference, so the script prompts for sign-in on first run rather than failing silently.

## [3.2.0] - 2026-02-03

> Historic version: v16.1

### Added

- `get_youtube_api_key()` function that resolves `YOUTUBE_API_KEY` from either a plain string or a 1Password secret reference (`op://`), enabling secrets to be stored in 1Password instead of plaintext `.env` files.
- Missing chat event handlers: `_handle_member_milestone`, `_handle_gift_membership_received`, `_handle_membership_gifting`, `_handle_message_deleted`. These event types were silently falling through to the generic handler before.

## [3.1.0] - 2026-01-20

> Historic version: v16.0

### Added

- `extract_video_id()` function supporting standard, short, embed, and live URL formats; backward compatible with direct video ID input.
- `get_venv_activation_command()` function that detects the active virtual environment via `VIRTUAL_ENV` or `sys.prefix` vs `sys.base_prefix`, then locates the platform-appropriate activation script.
- `open_terminal_with_ytdlp()` function that automatically opens a new terminal window and starts `yt-dlp --live-from-start` — supports macOS (AppleScript/Terminal.app), Linux (gnome-terminal, konsole, xterm), and Windows (cmd). Prepends venv activation when applicable.
- Optional video download toggle: prompt `Download video as well? (y/n) [y]:` after entering video ID, so chat capture can be restarted independently while a video download is already running.
- Streamlined workflow: both video download and chat capture now start automatically without a separate confirmation prompt.

### Changed

- Input prompt changed from `Enter video ID:` to `Enter YouTube URL or video ID:`.

## [3.0.0] - 2026-01-06

> Historic version: v15

### Added

- `QuotaManager` class for cross-session, file-locked API quota tracking stored in `.youtube_quota.json`. Uses `fcntl` file locking on Unix for multi-process safety; falls back gracefully on Windows.
- `YouTubeLiveChatFetcher` refactored to use `QuotaManager` for all API calls via `_execute_quota_guarded_request()`.
- Dynamic polling interval calculation (`_calculate_polling_interval()`) based on remaining quota and expected stream duration.
- `register_session()` call at stream start to log expected duration against quota budget.

### Changed

- Quota management moved from simple per-session counter to persistent cross-process file-backed store (`.youtube_quota.json`).

## [2.12.0] - 2025-01-21

### Changed

- Script renamed from `youtube_live_chat_fetcher14.py` to `livechat.py`.

## [2.11.1] - 2024-09-15

> Historic version: v14

### Added

- Committed to this repository as `youtube_live_chat_fetcher14.py`.
- Based on v13 with same quota management approach and all prior features intact.

## [2.11.0] - 2024-09-14 _(file timestamp)_

> Historic version: v13

### Added

- Proactive quota management in `__init__`: `MAX_DAILY_QUOTA` (10,000), `LIVE_CHAT_MESSAGES_COST` (5 per call), `videos_list_cost` (1 per call).
- Pre-calculated maximum allowed API calls based on configurable expected stream duration (default 4 hours).
- Dynamic polling interval enforced (minimum 5 seconds) to spread quota evenly across the stream.
- Per-call quota counter incremented after each `liveChatMessages.list` call; loop breaks if maximum reached.

## [2.10.0] - 2024-09-14 _(file timestamp)_

> Historic version: v12

### Added

- Termination reason tracking: `termination_reason` variable captures why collection stopped.
- Final row written to CSV with the termination reason (quota exhausted, live chat ended, user interrupt, unexpected error), providing an audit trail for debugging.

## [2.9.0] - 2024-09-14 _(file timestamp)_

> Historic version: v11

### Added

- `QuotaExceeded` exception raised when `quotaExceeded` error reason is returned by the API.
- `UnrecoverableAPIError` exception raised for any other API error that cannot be retried.
- Unified catch block for all three custom exceptions (`LiveChatEnded`, `QuotaExceeded`, `UnrecoverableAPIError`).

## [2.8.0] - 2024-09-14

> Historic version: v10

### Added

- `LiveChatEnded` exception raised when the API returns a `liveChatEnded` error reason, enabling graceful loop exit when a stream ends naturally.
- Enhanced `_handle_http_error()` to extract `reason` and `message` fields from error details.

## [2.7.1] - 2024-09-14 _(file timestamp)_

> Historic version: v9

### Changed

- Logging format simplified to `%(message)s` only, removing redundant timestamp and level prefix from terminal output.
- Chat messages printed via `print()` rather than `logging.info()` for cleaner console display.
- `file_handle.flush()` used in place of `writer.flush()` for more reliable periodic disk writes.

## [2.7.0] - 2024-09-14 _(file timestamp)_

> Historic version: v8b — ChatGPT o1-preview optimization of v8a.

### Added

- `logging` module replacing print statements for info/error output.
- `maxResults=200` added to all `liveChatMessages.list` API calls for better throughput.

### Changed

- Architecture changed from buffering all messages in memory to streaming directly to an open CSV file handle with periodic `flush()`.
- Polling interval fallback changed from hardcoded value to `pollingIntervalMillis` with a 2,000ms default.
- Error handling improved: checks HTTP status codes (403, 429) and decodes bytes responses before parsing.

### Removed

- `is_running` state flag and `_cleanup()` method introduced in v8a (found to be unnecessary and buggy).

## [2.6.0] - 2024-09-08 _(file timestamp)_

> Historic version: v8a — Marked as "does not work properly" — abandoned approach.

### Added

- `is_running` state flag and `_cleanup()` method for graceful shutdown on interrupt.

## [2.5.0] - 2024-09-08

> Historic version: v7

### Changed

- **Major refactor:** all logic moved into `YouTubeLiveChatFetcher` class.
- Message type dispatch replaced with a dict mapping event type strings to private handler methods: `_handle_text_message()`, `_handle_super_chat()`, `_handle_super_sticker()`, `_handle_new_sponsor()`, `_handle_other_event()`.
- Main loop broken into: `_get_live_chat_id()`, `_get_initial_chat_response()`, `_get_next_chat_response()`, `_process_chat_response()`, `_handle_http_error()`, `_print_chat_message()`.
- Full type hints added throughout (`Dict[str, Any]`, `tuple[str, str]`, etc.).

### Added

- Console instructions for running `yt-dlp` in parallel to download the stream.

## [2.4.0] - 2024-09-06

> Historic version: v6

### Added

- `SuperChat Amount` column in CSV output.
- `get_chat_message()` now returns `superchat_amount` separately from message text.
- `superChatEvent`: extracts `userComment` and `amountDisplayString`.
- `superStickerEvent`: extracts sticker `altText` and amount.
- Dedicated print format for superchat events showing amount alongside message.

## [2.3.0] - 2024-09-06 _(file timestamp)_

> Historic version: v5

### Added

- `pytz` and `dateutil` timezone handling; `convert_to_eastern()` converts API UTC timestamps to US/Eastern.
- `get_chat_message()` function dispatching on event type: `textMessageEvent`, `superChatEvent`, `superStickerEvent`, `newSponsorEvent`, and a generic fallback.
- `Message Type` column added to CSV.
- Try/except around per-message processing to handle `KeyError` gracefully without stopping the session.

## [2.2.0] - 2024-08-11

> Historic version: v4

### Added

- CSV export via `save_chat_to_file()`: writes Timestamp, Author, Message rows.
- Periodic flush every 5 minutes (configurable `save_interval`).
- User input prompt for `video_id` instead of hardcoded value.
- Finally block saves any remaining buffered messages on exit.
- CSV filename includes timestamp.

---

## Pre-repository versions

### [2.1.0] - 2024-08-11 _(file timestamp)_

> Historic version: v3

### Added

- `pollingIntervalMillis` from API response read and respected as sleep duration.
- Rate limit detection: checks for `rateLimitExceeded` reason in HTTP errors and sleeps before retrying.

### [2.0.0] - 2024-08-11 _(file timestamp)_

> Historic version: v2

### Changed

- Authentication switched from OAuth 2.0 (`google_auth_oauthlib`) to API key via `.env` file and `python-dotenv`.

### [1.0.0] - 2024-08-11 _(file timestamp)_

> Historic version: v1

### Added

- Initial script.
- OAuth 2.0 authentication.
- Basic `liveChatMessages.list` polling with `nextPageToken` pagination.
- Console output of chat messages.
- Basic `HttpError` handling.
