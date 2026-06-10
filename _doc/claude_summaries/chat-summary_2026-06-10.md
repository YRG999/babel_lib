# Chat Summary — 2026-06-10

## 1. youtube-downloader-app security review and bug fixes

Reviewed all of `youtube-downloader-app/` (13 files) for security and correctness issues, then applied the approved fixes (security + bugs; larger quality refactors and CSV formula-escaping deliberately skipped).

### Security fixes

- **`downloader.py`** — removed `nocheckcertificate: True` (TLS verification re-enabled for all yt-dlp traffic); switched `remote_components` from `ejs:npm` to `ejs:github`, the source recommended by yt-dlp's own warning.
- **`kick_live_downloader.py`** — the printed ffmpeg command now redacts the `-headers` value, which contained live Kick session cookies.
- **`firefox_cookie_export.py`** — `cookies.txt` is created with `0600` permissions.
- **`main.py` / `kick_vod_downloader.py`** — yt-dlp subprocess calls pass `--` before the URL to block argument injection (e.g. a `--exec=...` "URL").
- **Requirements** — app and root `requirements.txt` now pin minimum versions and include the previously missing `playwright` (+ `click` at root).
- **CSV/formula injection** — documented (README "Opening chat CSVs safely") rather than escaped, to keep chat data verbatim for analysis (user's choice).

### Bug fixes

- **`kick_live_downloader.py`** — ffmpeg headers used literal `\r\n` text (double-escaped in the f-string) instead of real CRLF, so UA/Referer/Cookie headers were sent mangled.
- **`add_vod_offset.py`** — `NameError` on header-only CSV (loop variable referenced after empty loop).
- **`filter_chat.py`** — crash on blank `vod_offset` rows; such rows now keep the emote/repetition filters and skip the time-window filters.
- **`kick_vod_downloader.py`** — `fetch_with_retry` raises after exhausting retries on repeated 429s instead of silently returning `{}`.
- **`livechat_to_csv.py`** — timestamps rendered in UTC (was local time, inconsistent with the Kick chat CSV).
- **Deleted `src/comments.py`** — legacy, unused by `main.py`, and broken (`.strftime()` called on a string; `return` without value used as a filename).

### Verification

- `py_compile` clean on all sources.
- End-to-end `--transcript-only` download of a short YouTube video succeeded with TLS verification on and `ejs:github` (JS challenge solved via deno).
- `filter_chat.py` and `add_vod_offset.py` ran cleanly on synthetic blank-offset / header-only CSVs.
- Cookie export against a synthetic profile produced a `-rw-------` file.

### Docs updated

`youtube-downloader-app/CHANGELOG.md` (released as **2.3.0** — bundles the pending Kick VOD routing feature with this session's Security/Fixed/Removed entries), `README.md`, `CLAUDE.md`, both `requirements.txt` files.

## 2. Security-concept explanations added to programming_reference.md

Added a "Security concepts" section to `_doc/programming_reference.md` explaining each of the 2.3.0 security fixes for a reader with an intro-Python background (MIT 6.0001/6.0002-level, long ago): TLS certificate verification and MITM attacks, supply-chain risk of remote code components, why secrets must not be printed to the terminal, Unix file permissions and `0600`, argument injection and the `--` separator, dependency pinning, and CSV/formula injection (documented rather than fixed, to keep chat data verbatim).

## 3. Security Practices section added to root CLAUDE.md

Added a "Security Practices" section to the root `CLAUDE.md` codifying the rules established by the 2.3.0 security review: secrets/cookies stay out of code, git, and logs (cookie files 0600 and gitignored); never disable TLS verification; yt-dlp `remote_components` stays on `ejs:github`; subprocess list-args with `--` before user-supplied URLs; redact credentials in debug output; `>=` version pins with deps added to both submodule and root requirements; chat CSVs contain untrusted text (no formula escaping, don't open in Excel). Added a PII rule: redact personally-identifiable/private information from anything pushable to GitHub (code, docs, summaries, commit messages); private items recorded for the user must go in a gitignored location (e.g. `_notes/`), verified with `git check-ignore` before writing. Also updated the Setup section to note `playwright install firefox`, and closed two `.gitignore` gaps: generic `cookies.txt` (default output of `firefox_cookie_export.py`) and `youtube-downloader-app/output*/` / `kick_output*/` (main.py creates output folders in the app directory, one level above the previously ignored `src/` patterns).

## 4. `--comments-only` flag added to youtube-downloader-app

Investigated two questions: (a) the deleted `comments.py` *was* intended as a comments-only downloader, but the app copy was never wired to `main.py`, had no `__main__` block, and was broken by a string/datetime mix-up — the working standalone original still exists at `ytdownload/comments.py`; (b) there is no live-chat/comments overwrite conflict — live chat goes to `.live_chat.json`, comments into `.info.json`, and the existing `--comments` flag (off by default) downloads both alongside the video. Added a new `--comments-only` flag to `main.py`/`downloader.py` (mutually exclusive with `--metadata-only`/`--transcript-only`): downloads only comments via `getcomments` + `writeinfojson` and extracts to `<title>_comments.csv`. Initially the intermediate `.info.json` was deleted; per user request it is now kept alongside the CSV for debugging or re-extracting later. Verified end-to-end on a 15-comment video (15 CSV rows; output folder contains the CSV plus the kept info JSON). README documents the flag and the live-chat-vs-comments explanation; released in CHANGELOG as **2.4.0**.

## 5. MIT Python course links added to programming_reference.md

Added the MIT 6.0001 / 6.0002 (Fall 2016) OCW courses to the Links section with one-sentence descriptions, noting they are good Python-learning resources but date from 2016, plus their updated successors as of 2026: OCW 6.100L (Fall 2022, post-renumbering) and the actively maintained MITx 6.00.1x / 6.00.2x courses on edX. All five URLs verified returning 200.
