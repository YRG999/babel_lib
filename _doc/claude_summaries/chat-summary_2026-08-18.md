# Chat summary — 2026-08-18

## Session 1

### Fixed YouTube 403 Forbidden downloads (youtube-downloader-app v2.4.2)

- **Problem:** `python main.py "https://www.youtube.com/watch?v=..."` failed with `ERROR: unable to download video data: HTTP Error 403: Forbidden`, with or without `--cookies`. Format listing worked; only the media fetch 403'd.
- **Diagnosis:** yt-dlp was already at the latest version (2026.7.4); `yt-dlp -v` showed `PO Token Providers: none`. YouTube now requires a GVS PO token to serve media URLs. Forcing `player_client=android` worked for video but lost automatic captions, so it was rejected as a workaround.
- **Fix (no code changes):** installed the yt-dlp-recommended [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) plugin (1.3.1) into the shared venv, in script mode: cloned and built its generation script at the default location `~/bgutil-ytdlp-pot-provider` (`npm ci && npx tsc`, Node ≥ 20). yt-dlp auto-detects both the plugin and the script.
- **Verified (partially — see second cause below):** provider now registers (`bgutil:script-node` / `bgutil:script-deno`) and small test fetches (`--test`, 10 KB) succeed where they previously 403'd. Caption listing on a captioned video confirmed transcripts still work; the originally requested video simply has no automatic captions (livestream VOD, live chat only).
- **Second cause found:** full-length downloads still 403'd — YouTube caps the only available https media URLs (from the `android_vr` client, which cannot get a bgutil PO token; requirement introduced 2026-08-02, [yt-dlp #17348](https://github.com/yt-dlp/yt-dlp/issues/17348)) at ~400 KB for this connection, because the SABR-only experiment ([yt-dlp #12482](https://github.com/yt-dlp/yt-dlp/issues/12482)) strips the web clients' normal URLs. Ruled out via testing: live chat traffic, elapsed time, cached visitor ID (`--rm-cache-dir`), a different VPN exit (both commercial-VPN exits behaved identically), HLS fallback (not offered; `ios` HLS needs an unsupported PO token variant), HTTP chunking (64 KB chunks died at ~400 KB), and the supposedly token-exempt format 18 (still 403s).
- **Resolution — `--sabr` flag (v2.5.0):** installed the SABR dev build of yt-dlp ([PR #13515](https://github.com/yt-dlp/yt-dlp/pull/13515)) in a separate gitignored `venv-sabr`; new `--sabr` flag in `main.py` routes the video download through it as a subprocess (security practices followed: list args, `--` before URL). SABR is not subject to the cap. Two sub-issues solved: (a) SABR video streams re-validate the PO token at ~5 MB and reject bgutil's synthetic tokens — fixed by using `yt-dlp-getpot-wpc` (browser-attested tokens via a logged-out throwaway Chrome; bgutil must be uninstalled from `venv-sabr` since it outranks wpc); (b) `nodriver` 0.50.3 ships a Latin-1 byte in `cdp/network.py` breaking the plugin import — fixed by a one-time UTF-8 re-encode (documented in README). Verified end-to-end on the VPN: full video + live chat + metadata download via `python main.py --sabr <url>`.
- **Code changes (`downloader.py`):** the default (full) mode now runs two yt-dlp passes — the video alone first, immediately after its URLs are extracted, then metadata + subtitles + live chat (`skip_download`) — and the video pass sets `check_formats: 'selected'` to skip outright-dead format URLs. Single-pass behavior of `--metadata-only`, `--transcript-only`, and `--comments-only` is unchanged.
- **Files changed:**
  - `requirements.txt` and `youtube-downloader-app/requirements.txt` — added `bgutil-ytdlp-pot-provider>=1.3.1`
  - `youtube-downloader-app/src/downloader.py` — two-pass download + `check_formats` (see above)
  - `youtube-downloader-app/src/main.py` — new `--sabr` flag + `_download_youtube_sabr()` subprocess path with setup guidance
  - `youtube-downloader-app/README.md` — new Installation step 4 (PO token script), `--sabr` option row, and "SABR downloads" section (setup, wpc provider, nodriver fix, TODO to retire `venv-sabr` after PR #13515 merges)
  - `youtube-downloader-app/CHANGELOG.md` — 2.4.2 (both causes) and 2.5.0 (`--sabr`) entries
  - `CLAUDE.md` (root) and `youtube-downloader-app/CLAUDE.md` — PO token provider + `venv-sabr` in external tools/dependencies
  - `.gitignore` — added `venv-sabr/`
  - `_doc/programming_notes.md` — new dated entry "YouTube 403 Forbidden: missing PO token provider" covering both causes and the SABR resolution, including a security review of `yt-dlp-getpot-wpc` (source-verified profile isolation, guest-only sessions, attack surface, supply chain) and an "In plain English" subsection for a non-technical audience
- **Cookies note:** `--cookies` reads live Firefox cookies and only helps while actually logged in to YouTube in Firefox — yt-dlp warns "The provided YouTube account cookies are no longer valid" when the browser session has expired or rotated.
- **Upstream bug identified:** the nodriver 0.50.3 Latin-1 byte in `cdp/network.py` is already reported upstream as [nodriver#35](https://github.com/ultrafunkamsterdam/nodriver/issues/35) (open since 2026-03-31, no maintainer response; reported on Linux, reproduced here on macOS — it's in the published wheel). Linked from the README "SABR downloads" section and the programming_notes entry instead of filing a duplicate.

## Session 2

### Fixed silent failures in `--transcript-only`/`--metadata-only`/`--comments-only` (v2.5.1)

- **Problem:** `python main.py --transcript-only "<youtube shorts URL>"` produced an empty output folder but still printed `"All output files saved in: output1"`. The video does have English auto-generated captions.
- **Diagnosis:** reproducing the exact yt-dlp options from `downloader.py` (both via the CLI and the Python API directly) downloaded the transcript successfully, so the fetch logic itself was correct — the empty folder was most likely a one-off hit from the same PO-token issue fixed earlier today (Session 1), not a code bug. But the investigation surfaced a real robustness gap: `downloader.py` set `ignoreerrors: True` and `no_warnings: True`, `convert_transcripts()` silently no-op'd on an empty `.vtt` glob, and `main.py`'s `finally` block always printed the success message — so any future failure in these three modes would look identical to success with no signal anything went wrong.
- **Fix:** removed `no_warnings: True` so yt-dlp's own warnings print; `download_video_info_comments()` now checks `ydl.download()`'s return value and prints an explicit warning on failure (kept `ignoreerrors: True` so one bad URL doesn't abort the rest); `convert_transcripts()` now reports when no `.vtt` files are found; the final message now warns instead of claiming success when the output folder ends up empty. Verified both the success path (transcript downloads and converts cleanly) and the failure path (an invalid video ID now surfaces `ERROR: ... Video unavailable`, the new download-failure warning, the no-`.vtt`-found warning, and the empty-folder warning, instead of a silent false "success").
- **Bonus fix found via the above:** removing `no_warnings` exposed that `'remote_components': 'ejs:github'` in `downloader.py` was a bare string, which yt-dlp iterated character-by-character and rejected in full (`WARNING: Ignoring unsupported remote component(s): j, g, t, u, e, b, h, :, i, s`). Changed to `['ejs:github']`. This had silently defeated the security-recommended remote-components setting since it was added.
- **Files changed:** `youtube-downloader-app/src/downloader.py`, `youtube-downloader-app/src/main.py`, `youtube-downloader-app/CHANGELOG.md`.

## Session 3

### Light-touch documentation consolidation

Surveyed all doc files in the repo (root/submodule `README.md`/`CLAUDE.md`/`CHANGELOG.md`, `_doc/programming_notes.md`, `_doc/programming_reference.md`, `_doc/claude_summaries/`) in response to a question about whether they could be consolidated. Conclusion: the file types are mostly non-duplicative (different altitudes — session diary vs. distilled troubleshooting vs. concept reference vs. usage vs. agent context), so no file types were merged. Applied targeted fixes instead:

- `_doc/programming_notes.md` — added a `**Session:**` cross-reference link to the corresponding `claude_summaries` file for the 4 entries whose existing date header matches an existing session-summary file (YouTube 403, Kick VOD 404, Claude Code custom skills, Claude Code skills overview).
- Root `CLAUDE.md` — replaced the restated `_doc/` file list in "## Documentation" with a one-line pointer to `README.md`'s "Additional documentation" section, keeping `README.md` as the single canonical index.
- `_doc/README.md` — the `claude_summaries/` table was stale (only 4 of 16 session files listed, last updated 2026-03-28); added the 12 missing rows (2026-03-29 through 2026-08-18) with one-line descriptions.
- Deleted `_notes/convert_to_csv/README.md` — a gitignored/untracked leftover that explicitly documented itself as superseded by `youtube-study/convertcsv/`.
- Ran `markdownlint-cli2` on all edited files; 0 issues.

**Aside noticed, not fixed (out of scope):** `_doc/programming_notes.md` is tracked by git as `_doc/Programming_notes.md` (capital P) while the file on disk is lowercase — likely a case-insensitive-filesystem artifact from an earlier rename. Works fine on macOS but would break relative links (including the ones added this session) on a case-sensitive filesystem like Linux CI. Worth a `git mv` cleanup in a future session.

## Session 4

### Filename-case fix and a new doc-maintenance rule

- Fixed the `_doc/Programming_notes.md` → `_doc/programming_notes.md` case mismatch found in Session 3: renamed via a two-step `git mv` (through a temporary name, since the source and destination differ only in case on this case-insensitive filesystem). `git status` confirmed a clean rename with zero content changes.
- Added a rule to `CLAUDE.md` § "Session Summaries": after writing a *new* `chat-summary_YYYY-MM-DD.md` file, add a row for it to the `claude_summaries/` table in `_doc/README.md` (not needed when only appending a section to an existing day's file, since that file already has a row) — to prevent the table from going stale again the way it had in Session 3.
