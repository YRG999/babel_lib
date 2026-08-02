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

> **Analysis tools** (`filter_chat.py`, `add_vod_offset.py`, `timestamp_converter.py`) have moved to [`youtube-study/analysis/`](../youtube-study/analysis/).

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
- `playwright` — headless Firefox for Kick live fallback (`playwright install firefox` after pip install)

## Running

```zsh
# YouTube video (always quote the URL — ? is a zsh glob wildcard)
python src/main.py "https://www.youtube.com/watch?v=VIDEO_ID"
python src/main.py --metadata-only --comments "https://www.youtube.com/watch?v=VIDEO_ID"
python src/main.py --transcript-only "https://www.youtube.com/watch?v=VIDEO_ID"
python src/main.py --comments-only "https://www.youtube.com/watch?v=VIDEO_ID"

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
- **English subtitles:** YouTube returns subtitles with locale codes like `en-US`, `en-GB`, `en-AU`. The downloader tries all variants (`en`, `en-US`, `en-GB`, `en-AU`) to maximize compatibility.
- **Output folders:** YouTube → `outputN/`; Kick VOD → `kick_outputN/`. A new folder is created per run.
- **Kick VOD chat API:** `GET web.kick.com/api/v1/chat/{channel_id}/history?start_time=ISO8601`. Time-windowed polling in 5-second windows from `start_time` to `start_time + duration`. 300 ms delay between requests is safe; increase with `--chat-delay` if 429s appear.
- **Kick VOD metadata structure:** All stream fields (`channel_id`, `start_time`, `duration`, `channel`) are nested under `"livestream"` in the `/api/v1/video/{uuid}` response, not at the top level.
- **Kick UUIDv7 video URLs:** Kick's frontend now uses UUIDv7 video IDs in `/videos/` URLs (they start with a timestamp, e.g. `019f...`), but `/api/v1/video/{uuid}` — also used internally by yt-dlp — only accepts legacy UUIDv4 IDs. On a 404, `kick_vod_downloader.py` decodes the ms-epoch timestamp from the UUIDv7's first 48 bits and matches it (±5 s) against `start_time` in `GET kick.com/api/v2/channels/{slug}/videos` to recover the legacy `video.uuid`, which is then used for metadata and for the yt-dlp URL. That listing returns only the latest 30 VODs and ignores pagination params, so older VODs with new-style URLs cannot be resolved. **TODO (check back after 2026-08):** upstream fix tracked in [yt-dlp #17284](https://github.com/yt-dlp/yt-dlp/issues/17284) — still open as of 2026-08-02; when merged, update yt-dlp and re-test whether the UUID resolution step is still needed for the video download (it will still be needed for metadata/chat).
- **Kick `duration` field:** May be seconds or milliseconds. Values > 259200 (3 days in seconds) are treated as milliseconds and divided by 1000.
- **`vod_offset` column:** First column of `<title>_chat.csv`. Formatted `H:MM:SS`. Gives the playback position in the video for each chat message: `message_timestamp − vod_start_time`. Use it to seek directly in VLC/mpv/video editors.
- **Comments and channels:** `--comments` only processes the most recently created `.info.json`. Do not use `--comments` when downloading a channel (multiple videos).
- **Kick live stream fallback:** `main.py` detects `kick.com/<username>` URLs (not VOD/clip paths), tries yt-dlp, then calls `download_kick_live()` from `kick_live_downloader.py`. If both fail, run `kick_live_downloader.py --headful` directly to bypass Cloudflare.
- **CSV safety:** chat messages/usernames are written to CSVs verbatim (no formula-prefix escaping, by design — data is used for analysis). Don't open chat CSVs directly in Excel; see the README "Opening chat CSVs safely" section.
