# Chat Summary — 2026-03-26

## Overview

This session added Kick.com VOD and live stream download support to `youtube-downloader-app`, reorganised the Kick-related source files, and consolidated documentation.

---

## 1. Research: yt-dlp and Kick.com chat

**Question:** Can yt-dlp download Kick.com livestream chat?

**Answer:** No. yt-dlp's `kick.py` extractor supports VODs, clips, and live streams (video only) but has no chat extraction. Kick does not expose a built-in chat replay API in the same way YouTube does.

---

## 2. Research: Kick.com VOD chat replay API

**Question:** Is there an API to extract replayed chat from Kick.com VODs?

**Findings:**

- Kick does replay chat for VODs.
- Undocumented but functional endpoint:

  ```txt
  GET https://web.kick.com/api/v1/chat/{channel_id}/history?start_time={ISO8601_UTC}
  ```

- `channel_id` is the numeric ID from VOD metadata (not the username slug).
- `start_time` format: `2024-01-15T20:00:00.000Z`
- Response: `{ "data": { "messages": [...], "cursor": "..." } }`
- Pagination: time-based, not cursor-based — iterate in 5-second windows from stream start to end.
- Rate limits: Kick temp-bans IPs that send requests too quickly; 300 ms delay between requests is safe.
- Reference implementation: [VXsz/ReKick](https://github.com/VXsz/ReKick) (Go).

VOD metadata (including `channel_id`, `start_time`, `duration`) is available from:

```txt
GET https://kick.com/api/v1/video/{uuid}
```

---

## 3. New file: `kick_vod_downloader.py`

**File:** `youtube-downloader-app/src/kick_vod_downloader.py`

A new standalone CLI tool that, given a Kick VOD URL, downloads the video and the full chat history.

### How it works

1. Parses the UUID from the VOD URL (`/videos/<UUID>`).
2. Fetches VOD metadata from `kick.com/api/v1/video/{uuid}` to get `channel_id`, `start_time`, and `duration`.
3. Downloads the video via `yt-dlp`.
4. Polls `web.kick.com/api/v1/chat/{channel_id}/history` in 5-second windows from start to end.
5. Deduplicates messages by ID, sorts chronologically, writes NDJSON + CSV.
6. Saves raw VOD metadata to `metadata.json`.
7. All output goes to a new `kick_outputN/` folder.

### Usage

```zsh
python src/kick_vod_downloader.py "https://kick.com/username/videos/UUID"
python src/kick_vod_downloader.py --chat-only "https://kick.com/username/videos/UUID"
python src/kick_vod_downloader.py --video-only "https://kick.com/username/videos/UUID"
python src/kick_vod_downloader.py --chat-delay 500 "https://kick.com/username/videos/UUID"
```

### Options

| Option | Description |
| --- | --- |
| `--video-only` | Skip chat, download video only |
| `--chat-only` | Skip video, download chat only |
| `--chat-delay N` | ms between chat API requests (default 300, min 100) |

### Output files

| File | Contents |
| --- | --- |
| `metadata.json` | Raw VOD metadata |
| `<title>_chat.csv` | timestamp, username, user_id, message, type, badges, color, amount, message_id, metadata |
| `<title>_chat.ndjson` | Raw messages, one JSON object per line |
| `<title>.mp4` | Video (unless `--chat-only`) |

### Notes

- Emotes appear as `[emote:ID:name]` in message content.
- Kick's `duration` field has been observed in both seconds and milliseconds; the script auto-detects the unit.
- Retry logic: up to 5 attempts with exponential backoff; 429 responses trigger an extended wait.

---

## 4. Rename: `kick_downloader.py` → `kick_live_downloader.py`

Renamed via `git mv` to distinguish the live stream downloader from the new VOD downloader.

---

## 5. Refactor: `kick_live_downloader.py`

Two meaningful changes on top of the rename:

### m3u8 auto-detection

Previously `--m3u8` was required — the user had to find the stream URL manually via browser Network tab. Now it is optional. When omitted, a `context.on("request", ...)` listener intercepts the first `master.m3u8` URL the Kick player requests after page load (waits up to 15 s).

```python
def _on_request(request):
    if detected_m3u8["url"] is None and "master.m3u8" in request.url:
        detected_m3u8["url"] = request.url

context.on("request", _on_request)
```

### Callable function

Core logic extracted into `download_kick_live(page_url, m3u8_url=None, out=..., headful=False, ...)` returning `True`/`False`, so `main.py` can import and call it. The argparse CLI now delegates to this function.

---

## 6. Update: `main.py` — Kick live stream fallback

`main.py` now handles Kick live stream URLs by:

1. Detecting `kick.com/username` URLs (not VOD or clip paths) via regex.
2. Trying `yt-dlp` first (subprocess, checks exit code).
3. On failure, importing and calling `download_kick_live()` from `kick_live_downloader`.
4. If both fail, printing a clear error suggesting `--headful`.
5. Skipping YouTube-specific post-processing (transcript/livechat/comment conversion) for Kick URLs.

```python
def _is_kick_live_url(url):
    return bool(re.match(r"https?://(?:www\.)?kick\.com/[^/?#]+/?$", url))
```

---

## 7. Documentation consolidation

- Created `kick_vod_downloader_README.md` and `kick_vod_downloader_CHANGELOG.md` as standalone docs (later consolidated).
- Merged `kick_vod_downloader_CHANGELOG.md` into `youtube-downloader-app/CHANGELOG.md` under the `[2.1.0]` entry with granular sub-bullets.
- Merged `kick_vod_downloader_README.md` into `youtube-downloader-app/README.md` as a new `## Kick.com` section covering both live streams and VODs.
- Deleted both standalone `kick_vod_downloader_*.md` files.
- Updated `youtube-downloader-app/README.md` project structure table to list `kick_live_downloader.py` and `kick_vod_downloader.py`.
- Added `[2.1.0] - 2026-03-26` entry to `youtube-downloader-app/CHANGELOG.md`.

---

## Files changed

| File | Change |
| --- | --- |
| `youtube-downloader-app/src/kick_vod_downloader.py` | Created |
| `youtube-downloader-app/src/kick_live_downloader.py` | Renamed from `kick_downloader.py`; m3u8 auto-detection; callable function |
| `youtube-downloader-app/src/main.py` | Added Kick live stream detection and yt-dlp → Playwright fallback |
| `youtube-downloader-app/README.md` | Added `## Kick.com` section; updated project structure |
| `youtube-downloader-app/CHANGELOG.md` | Added `[2.1.0]` entry |
| `youtube-downloader-app/src/kick_vod_downloader_README.md` | Created then deleted (merged into README.md) |
| `youtube-downloader-app/src/kick_vod_downloader_CHANGELOG.md` | Created then deleted (merged into CHANGELOG.md) |

---

## 8. Bug fix: `kick_vod_downloader.py` — wrong metadata structure

**Error:** `Could not determine channel_id from VOD metadata.`

**Root cause:** The `/api/v1/video/{uuid}` endpoint nests all stream data under a `"livestream"` key. The code was reading `channel_id`, `session_title`, `start_time`, `duration`, and `channel` from the top level of the response, where they don't exist.

Actual response structure:

```json
{
  "uuid": "...",
  "source": "...",
  "livestream": {
    "channel_id": 668,
    "session_title": "...",
    "start_time": "2026-03-25T21:13:23+00:00",
    "duration": 12428000,
    "channel": { "id": 668, "slug": "xqc", ... }
  }
}
```

**Fix:** Extract `livestream = meta.get("livestream") or {}` first, then read all fields from `livestream` with fallback to the top level.

Also confirmed: `duration` is in milliseconds (12,428,000 ms ≈ 3.4 hours), and `start_time` uses `+00:00` timezone suffix — both already handled correctly by the existing parsing logic.

---

## 9. Type error fixes: `kick_vod_downloader.py`

Two type annotation errors fixed:

| Line | Error | Fix |
| --- | --- | --- |
| 39 | `params: dict = None` — `None` not assignable to `dict` | `params: dict \| None = None` |
| 257 | `int(channel_id)` — type checker saw `channel_id` as potentially `None` | Added `assert channel_id is not None` on the line above |

The assert on line 257 is safe: the earlier guard (`if not channel_id and not video_only: raise`) already guarantees `channel_id` is non-None at that point, but the assert narrows the type for the checker.

---

## 10. Feature: `vod_offset` column in Kick VOD chat CSV; docs and CLAUDE.md

**Question:** How do I match up the timestamps in the downloaded live chat with the timestamps in the downloaded VOD?

**Answer:** The chat CSV uses absolute UTC wall-clock timestamps; the video uses playback-relative timestamps. The mapping is:

```text
vod_playback_position = message_timestamp − vod_start_time
```

`vod_start_time` is stored in `metadata.json` under `livestream.start_time`.

**Change:** Added `vod_offset` as the first column of `<title>_chat.csv`. Formatted `H:MM:SS`. Computed from the raw `created_at` field on each message (not the pre-formatted timestamp string). Values are clamped to `max(offset, 0)` to handle any messages arriving slightly before the recorded start time.

Also created `youtube-downloader-app/CLAUDE.md` (modeled on `ytdownload/CLAUDE.md`) to give Claude standing context about the project. CLAUDE.md files are automatically loaded into Claude Code's context at the start of every session — what files exist, conventions, and important gotchas — so Claude does not need to rediscover them each session.

**Files changed:**

| File | Change |
| --- | --- |
| `youtube-downloader-app/src/kick_vod_downloader.py` | Added `vod_offset` computation and column in `download_chat()` |
| `youtube-downloader-app/README.md` | Updated VOD output table; added `vod_offset` explanation |
| `youtube-downloader-app/CHANGELOG.md` | Added `[2.1.1]` entry |
| `youtube-downloader-app/CLAUDE.md` | Created — purpose, key files, dependencies, running commands, important context |
| `_notes/claude/chat-summary_2026-03-26.md` | Updated (this entry) |
