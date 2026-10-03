# Chat summary — 2026-09-20

## Session 1

### Documented live-stream fragment 403s vs. the PO-token 403

- User reported `yt-dlp` printing "Got error: HTTP Error 403: Forbidden. Retrying fragment" during a `livechat.py` live capture while the download kept progressing. Diagnosed as expected, self-healing behavior: live-stream fragment URLs are short-lived and rotate, so yt-dlp's built-in per-fragment retry (`--fragment-retries`) occasionally has to re-fetch a fragment — unrelated to the project's documented permanent PO-token/VPN-cap 403 (`_doc/programming_notes.md`, 2026-08-18), which fails outright and doesn't self-heal via retry.
- Added a new "Live-stream fragment 403s ('Retrying fragment') vs. the PO-token 403" section to `_doc/programming_reference.md` (under "YouTube & yt-dlp"), with a plain-English explanation and a cross-link to the existing PO-token 403 entry in `programming_notes.md`, following the file's existing explanation pattern.
- **Files changed:** `_doc/programming_reference.md`.
