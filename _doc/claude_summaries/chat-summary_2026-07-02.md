# Chat Summary — 2026-07-02

## Session 1

### Kick VOD 403 fix (yt-dlp impersonation)

- Diagnosed `[kick:vod] ... HTTP Error 403: Forbidden`: Kick's Cloudflare protection requires yt-dlp browser impersonation via `curl_cffi`, which was not installed in the venv. Same problem/fix already logged in `_doc/programming_notes.md` → "Download kick videos".
- Installed `yt-dlp[default,curl-cffi]` in the venv; verified impersonation targets are now available (`yt-dlp --list-impersonate-targets`).
- Updated `requirements.txt` (root) and `youtube-downloader-app/requirements.txt`: `yt-dlp>=2024.5.7` → `yt-dlp[default,curl-cffi]>=2024.5.7` so the extra is included on fresh installs.
