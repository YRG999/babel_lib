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
