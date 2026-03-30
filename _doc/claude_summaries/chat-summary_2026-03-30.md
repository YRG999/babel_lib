# Chat Summary — 2026-03-30

## Overview

Debugging session for `kick_live_downloader.py --use-profile`. Six sequential errors resolved, cookie injection confirmed working. End-to-end download tested against a live stream — resolved three further ffmpeg issues (AAC bitstream, audio sync, interrupted output). Released as `[2.2.1]`. Also: CHANGELOG, README, and chat summary housekeeping.

---

## 1. Debugging `kick_live_downloader.py` — `--use-profile` errors

All fixes applied to `youtube-downloader-app/src/kick_live_downloader.py`. Errors tracked in `_notes/txt/error.txt` (untracked).

| Error | Root Cause | Fix |
| --- | --- | --- |
| 1 | `ModuleNotFoundError: playwright` | `pip install playwright && python -m playwright install` |
| 2 | `launch_persistent_context` timeout — headless renderer fails with real Firefox profile (`RenderCompositorSWGL`) | Force headful mode when `--use-profile` is set |
| 3 | Same GPU Helper / XPC timeout even with headful + copied temp profile | Dropped `launch_persistent_context` entirely; switched to extracting cookies via `browser_cookie3` and injecting into a regular headless context via `add_cookies` |
| 4 | `add_cookies` rejected session cookies — `expires` field omitted, Playwright defaulted to `0` internally which it rejects | Always set `expires` explicitly: positive int for persistent cookies, `-1` (Playwright sentinel) for session cookies |
| 5 | Same error persisted — bulk `add_cookies` gave no info on which cookie failed | Add cookies one at a time with per-cookie `try/except`; print name + expires on failure; skip cookies with missing name/domain |
| 6 | All 14 cookies skipped — `expires` values like `1765827144841` are milliseconds, Playwright expects seconds | If `expires > 32503680000` (year 3000 in seconds), divide by 1000 |

### Test run

Tested against a live Kick channel. Result: **14/14 cookies injected successfully (0 skipped)** — confirms the Error 6 fix works. m3u8 was not auto-detected because the stream was offline at the time.

A second test was run with a manually supplied m3u8 URL (obtained from devtools). Result: **403 Forbidden**. The m3u8 was an Amazon IVS signed URL — these are time-limited and IP-bound, so Kick session cookies don't authorize them. Manual `--m3u8` won't work for these URLs; auto-detection (letting the script intercept from the browser's own traffic) is the correct approach. Full end-to-end test still pending (requires a live stream).

### How to get the m3u8 manually (when needed)

Devtools → Network tab → filter by `m3u8` → reload page with player active → copy `master.m3u8` URL. Pass with `--m3u8 "..."`. Note: IVS-hosted streams won't work this way; auto-detection is required.

---

## 2. Code fix: `_close()` — `browser` potentially `None`

Fixed a type/runtime issue on what was line 97: `browser.close()` was called unconditionally in the `else` branch of `_close()`, but `browser` is initialized as `None`. Changed to `elif browser is not None: browser.close()`.

---

## 3. CHANGELOG updates

- `kick_live_downloader.py` fixes placed under `[Unreleased]` (not yet fully tested end-to-end).
- `filter_chat.py` placed under `[2.2.0] - 2026-03-30` (released).
- `[Unreleased]` entry for the ms→seconds cookie fix had "*(fix applied, not yet tested)*" note; removed after confirming cookies inject successfully.

---

## 4. Session cookie exposure note

A test run printed Kick session cookie values (including `session_token`, `cf_clearance`, KP cookies) in terminal output. Advised to log out and back in to Kick to rotate the session. Stripe cookies (`__stripe_mid`, `__stripe_sid`) are analytics-only and not a concern.

Claude Code does not persist terminal output beyond the local session JSONL file (`~/.claude/projects/<encoded-path>/<session-id>.jsonl`). The `/feedback` command should be avoided in any session where secrets were printed, as it sends the full conversation to Anthropic.

---

## 5. File housekeeping

- `_doc/claude_summaries/chat-summary_2026-03-29.md` moved from `youtube-downloader-app/_doc/claude_summaries/` to top-level `_doc/claude_summaries/`. The `youtube-downloader-app/_doc/` directory was deleted.
- Section 4 (kick_live_downloader debugging) was briefly moved from `chat-summary_2026-03-28.md` to `chat-summary_2026-03-29.md`, then reverted — it remains in `chat-summary_2026-03-28.md`.

---

## 6. Live stream download — ffmpeg fixes

After cookie injection was confirmed working (14/14), a full end-to-end test was run against a live stream. Three further ffmpeg issues were found and fixed:

| Issue | Fix |
| --- | --- |
| Output file unplayable after Ctrl+C — MP4 moov atom never written | Added `-movflags +frag_keyframe+empty_moov` to write index incrementally |
| `Malformed AAC bitstream` error — ADTS framing incompatible with MP4 container | Added `-bsf:a aac_adtstoasc` (later removed when audio re-encode was adopted) |
| Audio out of sync — HLS segment timestamp discontinuities cause drift when stream-copying audio | Switched to `-c:a aac` (re-encode audio); video remains `-c:v copy`. `-avoid_negative_ts make_zero` also added |

Download confirmed working after these fixes.

---

## 7. Output folder

Output is now saved to `kick_outputN/` (same pattern as `kick_vod_downloader.py`). Folder is created automatically inside `download_kick_live()` when `--out` has no directory component. Explicit paths (e.g. `--out /tmp/stream.mp4`) bypass folder creation.

---

## 8. Release `[2.2.1] - 2026-03-30`

All `kick_live_downloader.py` fixes moved from `[Unreleased]` to `[2.2.1]`. README updated with recommended workflow: supply m3u8 manually via devtools (quickest), with `--headful` as fallback for auto-detection.
