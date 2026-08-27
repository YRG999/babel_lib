# _doc

Documentation, reference notes, and session summaries.

## Files

| File | Contents |
| --- | --- |
| `programming_notes.md` | Troubleshooting log — dated problem/cause/fix entries. Add new entries here when you encounter and solve a specific problem. |
| `programming_reference.md` | Thematic reference — API links, how-to notes, and reference tables organized by topic. |

## Folders

### `claude_summaries/`

End-of-session summaries of work done with Claude Code. One file per day; new sessions append a numbered section to the existing file for that date.

| File | Contents |
| --- | --- |
| `chat-summary_2026-03-04_11-13-42.md` | Refactored `youtube-downloader-app/src/main.py` to a click CLI; updated README and created CHANGELOG; debugged zsh glob expansion issue with YouTube URLs; fixed markdown lint errors and reorganized `Programming_notes.md`; added Claude Code session log file info |
| `chat-summary_2026-03-26.md` | Added Kick.com VOD downloader (`kick_vod_downloader.py`) with full chat history via API polling; refactored `kick_live_downloader.py` with m3u8 auto-detection; added Kick live stream fallback to `main.py`; added `vod_offset` column to chat CSV; created `CLAUDE.md` |
| `chat-summary_2026-03-27.md` | Created `add_vod_offset.py` backfill script; code review and cleanup of all `src/` files (bug fixes, refactors, dead code removal) |
| `chat-summary_2026-03-28.md` | Claude Code skills overview; consolidated `add_vod_offset.py` into `youtube-downloader-app/src/`; reorganized programming notes into `_doc/` with `programming_notes.md` and `programming_reference.md` |
| `chat-summary_2026-03-29.md` | Added `filter_chat.py` Kick chat noise filter (emote/repetition/dedup/reaction-flood filters); updated docs |
| `chat-summary_2026-03-30.md` | Debugged `kick_live_downloader.py --use-profile` (six sequential cookie-injection errors); fixed ffmpeg live-download issues (moov atom, AAC bitstream, audio sync); released `[2.2.1]`; Claude Code version-management Q&A |
| `chat-summary_2026-03-31.md` | Cleaned up `ytdownload/` (deleted abandoned/redundant scripts, fixed deprecated `datetime` calls); corrected stale filename references in root `README.md` |
| `chat-summary_2026-04-02.md` | Added `--compare` bidirectional mode to `dir_compare.sh`; created its `README.md`/`CHANGELOG.md` |
| `chat-summary_2026-04-04.md` | Created root `CLAUDE.md`; renamed `ytdownload/claude.md` → `CLAUDE.md`; created `/summary` and `/docupdate` skills; added Claude Code custom-skills entry to `programming_notes.md` |
| `chat-summary_2026-05-13.md` | Fixed `--transcript-only` missing `en-US`/`en-GB`/`en-AU` subtitle variants; created `/commit` skill; released `[2.2.2]` |
| `chat-summary_2026-06-06.md` | Added Kick VOD auto-detection and `--video-only`/`--chat-only`/`--chat-delay` options to `main.py` |
| `chat-summary_2026-06-10.md` | Security review and bug-fix pass across `youtube-downloader-app/` (TLS verification, `ejs:github`, cookie file permissions, subprocess arg injection, dependency pinning); added Security Practices to root `CLAUDE.md` and Security concepts to `programming_reference.md`; added `--comments-only` flag; released `[2.3.0]`/`[2.4.0]` |
| `chat-summary_2026-06-30.md` | Created `youtube-study/word_frequency/word_freq.py`; created `youtube-study/` as a new top-level analysis hub and moved scripts from `ytdownload/`/`youtube-downloader-app/src/` into it |
| `chat-summary_2026-07-02.md` | Fixed Kick VOD 403 by installing `yt-dlp[default,curl-cffi]` for browser impersonation |
| `chat-summary_2026-08-02.md` | Fixed Kick VOD 404 for new UUIDv7 video URLs by resolving them to legacy UUIDs; released `[2.4.1]` |
| `chat-summary_2026-08-18.md` | Fixed YouTube 403 (missing PO token, then SABR-only IP capping) via `bgutil-ytdlp-pot-provider` and a new `--sabr` flag; released `[2.4.2]`/`[2.5.0]`; fixed silent failures in `--transcript-only`/`--metadata-only`/`--comments-only` and a broken `remote_components` string, released `[2.5.1]` |
| `chat-summary_2026-08-27.md` | Fixed orphaned Chrome processes from `--sabr`'s `wpc` PO token provider via process-group cleanup in `_download_youtube_sabr()`; released `[2.5.2]` |

### `2024/`

Reference notes and local LLM experiment sessions.

| File | Contents |
| --- | --- |
| `Using_yt-dlp_cookies.md` | yt-dlp cookie usage reference — `--cookies-from-browser` syntax, supported browsers, profile paths, and troubleshooting |
| `mistral20240725.md` | Local Mistral session (`ollama run mistral`) exploring letter counting and longest words without repeating letters |

### `2023/`

Early experiment notes and AI-assisted debugging sessions.

| File | Contents |
| --- | --- |
| `Claude_debugging.md` | Claude debugging session for Python `exec()` interop — passing modules and input shims into namespaced execution |
| `chatGPT_documentation.md` | ChatGPT session building a random sentence generator with grammar validation (`language_tool_python`) |
