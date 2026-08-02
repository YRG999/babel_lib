# Chat summary — 2026-08-02

## Session 1

### Kick VOD 404 fix: new UUIDv7 video URLs (v2.4.1)

- Diagnosed a `404 Client Error` from `kick.com/api/v1/video/{uuid}` for a VOD that played fine in a browser: Kick's frontend now uses UUIDv7 video IDs in `/videos/` URLs, while the v1 metadata endpoint (also used internally by yt-dlp's Kick extractor) only accepts legacy UUIDv4 IDs. Verified live that the endpoint itself still works for legacy IDs.
- `youtube-downloader-app/src/kick_vod_downloader.py`:
  - `parse_vod_uuid` → `parse_vod_url`, now also extracting the channel slug.
  - New `resolve_legacy_uuid()`: decodes the ms-epoch timestamp from the UUIDv7's first 48 bits and matches it (±5 s) against `start_time` in `GET kick.com/api/v2/channels/{slug}/videos` to recover the legacy `video.uuid`. Triggered automatically when the v1 metadata fetch returns 404.
  - yt-dlp is now given a rebuilt URL containing the resolved legacy UUID (the original v7 URL would 404 inside yt-dlp too).
  - `fetch_with_retry` no longer retries 404s (previously 5 attempts with backoff); other 4xx (e.g. transient Cloudflare 403s on the chat API) still retry. New `KickNotFoundError` distinguishes the 404 case.
- Limitation discovered while probing: the channel videos listing returns only the latest 30 VODs and ignores pagination params, so new-style URLs for older VODs fail with an explanatory error.
- Verified: v7 URL resolves and downloads chat; legacy v4 URL works unchanged with no resolution step; unresolvable v7 ID fails in ~1.5 s with a clear message.
- Docs updated: app `README.md` (both ID formats + latest-30 limitation), app `CLAUDE.md` (Important Context entry), app `CHANGELOG.md` (2.4.1), `_doc/programming_notes.md` (dated problem/cause/fix entry).
- Upstream status: the same breakage is yt-dlp issue [#17284](https://github.com/yt-dlp/yt-dlp/issues/17284) (open, no fix PR as of 2026-08-02) — Kick confirmed the URL-generation change. Check back later; once yt-dlp ships a fix, the rebuilt-URL step could pass the original URL again, but the metadata/chat side still needs our resolution. Reminder added to app `CLAUDE.md`.
