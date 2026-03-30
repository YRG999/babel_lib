# youtube-downloader-app

CLI tools for downloading YouTube and Kick.com videos, metadata, transcripts, and live chat.

## Purpose

- **YouTube downloads** — video, subtitles, live chat, comments, metadata via yt-dlp
- **Kick VOD downloads** — video + full chat history via Kick API time-windowed polling
- **Kick live streams** — yt-dlp with automatic Playwright + ffmpeg fallback
- **Post-processing** — VTT → text, live chat NDJSON → CSV, comment extraction

## Key Files

| File | Purpose |
| --- | --- |
| `src/main.py` | CLI entry point (click) — YouTube and Kick live stream URLs |
| `src/downloader.py` | yt-dlp download logic (video, metadata-only, transcript-only modes) |
| `src/kick_vod_downloader.py` | Kick VOD + full chat history downloader (standalone CLI) |
| `src/kick_live_downloader.py` | Kick live stream downloader — Playwright + ffmpeg, m3u8 auto-detection |
| `src/livechat_to_csv.py` | Convert yt-dlp live chat NDJSON to CSV |
| `src/vtt_to_text.py` | Convert VTT subtitle files to plain text |
| `src/remove_dupe_lines.py` | Deduplicate converted transcript lines |
| `src/extract_comments.py` | Extract comments from yt-dlp `.info.json` to CSV |
| `src/firefox_cookie_export.py` | Export Firefox cookies for yt-dlp authenticated downloads |
| `src/timestamp_converter.py` | EST ↔ epoch timestamp converter utility (interactive) |
| `src/add_vod_offset.py` | Backfill `vod_offset` column in existing Kick VOD chat CSVs |
| `src/filter_chat.py` | Filter emote-only, repetitive, and reaction-flood messages from Kick chat CSVs |
| `src/comments.py` | Legacy comment helpers (unused by main.py) |

## Dependencies

**External tools:**

- `yt-dlp` — video downloading
- `ffmpeg` — stream merging (required for MP4 output)
- `playwright` — Kick live stream fallback (headless browser)

**Python packages:**

- `click` — CLI framework
- `requests` — Kick API calls
- `pytz` — timezone handling
- `browser-cookie3` — Firefox cookie support

## Running

```zsh
# YouTube video (always quote the URL — ? is a zsh glob wildcard)
python src/main.py "https://www.youtube.com/watch?v=VIDEO_ID"
python src/main.py --metadata-only --comments "https://www.youtube.com/watch?v=VIDEO_ID"
python src/main.py --transcript-only "https://www.youtube.com/watch?v=VIDEO_ID"

# Kick live stream (yt-dlp first, Playwright fallback auto)
python src/main.py "https://kick.com/username"

# Kick VOD + full chat
python src/kick_vod_downloader.py "https://kick.com/username/videos/UUID"
python src/kick_vod_downloader.py --chat-only "https://kick.com/username/videos/UUID"
```

## Notes

| File | Purpose |
| --- | --- |
| `_doc/programming_notes.md` | Troubleshooting log — dated problem/cause/fix entries |
| `_doc/programming_reference.md` | Thematic reference — API links, how-to notes, reference tables |

## Important Context

- **Always quote YouTube URLs** in zsh — `?` in `?v=...` is a glob wildcard and causes `no matches found` before Python runs.
- **Output folders:** YouTube → `outputN/`; Kick VOD → `kick_outputN/`. A new folder is created per run.
- **Kick VOD chat API:** `GET web.kick.com/api/v1/chat/{channel_id}/history?start_time=ISO8601`. Time-windowed polling in 5-second windows from `start_time` to `start_time + duration`. 300 ms delay between requests is safe; increase with `--chat-delay` if 429s appear.
- **Kick VOD metadata structure:** All stream fields (`channel_id`, `start_time`, `duration`, `channel`) are nested under `"livestream"` in the `/api/v1/video/{uuid}` response, not at the top level.
- **Kick `duration` field:** May be seconds or milliseconds. Values > 259200 (3 days in seconds) are treated as milliseconds and divided by 1000.
- **`vod_offset` column:** First column of `<title>_chat.csv`. Formatted `H:MM:SS`. Gives the playback position in the video for each chat message: `message_timestamp − vod_start_time`. Use it to seek directly in VLC/mpv/video editors.
- **Comments and channels:** `--comments` only processes the most recently created `.info.json`. Do not use `--comments` when downloading a channel (multiple videos).
- **Kick live stream fallback:** `main.py` detects `kick.com/<username>` URLs (not VOD/clip paths), tries yt-dlp, then calls `download_kick_live()` from `kick_live_downloader.py`. If both fail, run `kick_live_downloader.py --headful` directly to bypass Cloudflare.

## Session Summaries

At the end of each session, add a summary of what was done to `_doc/claude_summaries/chat-summary_YYYY-MM-DD.md` using today's date. If a file for today already exists, append a new numbered section to it. If not, create it. Only include what is unique to the session — do not duplicate content already covered in a summary for the same date.
