# Chat summary — 2026-09-13

## Session 1

### Documented why bgutil's generation script lives outside any venv

- Answered a question about why `~/bgutil-ytdlp-pot-provider` (the PO-token generation script used by the `bgutil-ytdlp-pot-provider` yt-dlp plugin) lives in the home directory instead of inside `venv` or `venv-sabr`: the pip-installed plugin is Python and does live in the venv via `requirements.txt`, but its actual token-generation logic is a separate Node.js/TypeScript program (`npm ci && npx tsc`, Node ≥ 20) — a Python virtualenv has no mechanism for holding Node dependencies, so it can't live inside either venv. The home-directory path specifically is the plugin's own hardcoded default lookup location (per `youtube-downloader-app/README.md` Installation step 4 — "yt-dlp finds the script there automatically").
- Added a "Why bgutil's generation script lives outside any venv" subsection to `_doc/programming_reference.md` under "YouTube & yt-dlp", including a plain-English recap (matching the style already used in `_doc/programming_notes.md`'s "In plain English" sections) for a non-technical audience.
- **Files changed:** `_doc/programming_reference.md`.
