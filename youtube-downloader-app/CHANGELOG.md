# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.2] - 2026-08-27

### Fixed

- `--sabr`: the `yt-dlp-getpot-wpc` PO token provider (in `venv-sabr`) can fail to attach to the throwaway Chrome instance it just launched (`PoTokenProviderError('failed to start browser: ... Failed to connect to browser')`) and retries with a new one; because the exception fires before the plugin stores a reference to the failed browser, that Chrome process was never closed. `_download_youtube_sabr()` now runs the `venv-sabr/bin/yt-dlp` subprocess in its own process group (`start_new_session=True`) and kills any survivors in that group (`os.killpg(..., signal.SIGKILL)`) once it exits, cleaning up any such orphan. Silent in the common case (no leftovers); prints a warning to stderr only when it actually kills one.

## [2.5.1] - 2026-08-18

### Fixed

- `--transcript-only`, `--metadata-only`, and `--comments-only` could fail completely (e.g. a transient PO token error) and still print `"All output files saved in: outputN"`, because `downloader.py` set `ignoreerrors: True` and `no_warnings: True` on the yt-dlp options and swallowed the result, `convert_transcripts()` silently no-op'd when no `.vtt` files existed, and `main.py`'s `finally` block always printed the success message. Now: yt-dlp warnings are no longer suppressed, a non-zero return from `ydl.download()` prints an explicit warning, `convert_transcripts()` reports when no subtitle files were found, and the final message warns instead of claiming success when the output folder ends up empty.
- `downloader.py`: `'remote_components': 'ejs:github'` was a bare string, which yt-dlp iterated character-by-character (`WARNING: Ignoring unsupported remote component(s): j, g, t, u, e, b, h, :, i, s`) and rejected in full — it should be `['ejs:github']`. This had been silently defeating the security-recommended remote-components setting (see CLAUDE.md "Security Practices") since it was added; the warning was previously hidden by `no_warnings: True`.

## [2.5.0] - 2026-08-18

### Added

- `main.py`: new `--sabr` flag (YouTube full-download mode only) — downloads the video via YouTube's SABR streaming protocol using the dev build of yt-dlp ([PR #13515](https://github.com/yt-dlp/yt-dlp/pull/13515)) installed in a separate, gitignored `venv-sabr` virtualenv, leaving the pinned stable yt-dlp untouched. SABR is not subject to the per-URL data cap YouTube applies to regular https media URLs on distrusted IPs (see 2.4.2 below), making this the only working full-video path on VPN exits. Subprocess call follows the repo security practices (list args, `--` before the URL). Mutually exclusive with the `*-only` modes and Kick URLs. See README "SABR downloads" for one-time setup.
- PO tokens for the SABR path come from [yt-dlp-getpot-wpc](https://github.com/coletdjnz/yt-dlp-getpot-wpc) (browser-attested, via a logged-out throwaway Chrome instance) instead of bgutil: SABR video streams re-validate the token mid-stream and reject bgutil's synthetic tokens at ~5 MB ("This stream requires a GVS PO Token to continue and the one provided is invalid"). bgutil must not be installed in `venv-sabr` (it outranks wpc). Known issue documented in the README: `nodriver` 0.50.3 needs a one-time UTF-8 re-encode of `cdp/network.py`.

## [2.4.2] - 2026-08-18

### Fixed

- YouTube downloads failing with `ERROR: unable to download video data: HTTP Error 403: Forbidden` (with or without `--cookies`), while format listing still worked. Two independent causes, both required for the fix:
  1. **Missing PO token provider.** YouTube now requires a GVS PO token to serve media URLs, and no provider was installed (`yt-dlp -v` showed `PO Token Providers: none`). Fix: added the [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) plugin (`>=1.3.1`, recommended by the [yt-dlp PO-Token-Guide](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide)) to `requirements.txt`, used in script mode: its generation script must be cloned and built once at `~/bgutil-ytdlp-pot-provider` (Node.js ≥ 20) — see README Installation step 4. The plugin auto-registers with yt-dlp for both the library path (`downloader.py`) and the subprocess path (`main.py` Kick fallback).
  2. **Per-URL data cap on media URLs (IP-reputation enforcement).** Even with a valid PO token, YouTube served only the first few hundred KB of any media URL to this connection (a VPN exit IP), then 403'd: 10 KB test fetches always succeeded, full downloads always failed, and 64 KB-chunked downloads died after ~400 KB. This is server-side throttling of a distrusted IP, not something client code can bypass (HLS fallback was explored but YouTube stopped offering HLS manifests to the session, and the `ios` client's HLS needs a PO token variant the bgutil provider doesn't generate). Mitigations in `downloader.py`: the default mode is now split into two yt-dlp passes — the video alone first (its URLs are used immediately after extraction), then metadata + subtitles + live chat (`skip_download`) second — and the video pass sets `check_formats: 'selected'` to skip outright-dead format URLs (the small test fetch cannot detect the data cap itself). Single-pass behavior for `--metadata-only`, `--transcript-only`, and `--comments-only` is unchanged (they never download video). Full resolution requires a reputable IP (e.g. a different VPN exit or a direct connection).

## [2.4.1] - 2026-08-02

### Fixed

- `kick_vod_downloader.py`: support Kick's new-style UUIDv7 video URLs. Kick's frontend now puts UUIDv7 IDs in `/videos/` URLs, but the `api/v1/video/{uuid}` metadata endpoint (also used internally by yt-dlp) only accepts the legacy UUIDv4 IDs, so downloads failed with `404 Client Error`. On a 404, the downloader now decodes the timestamp embedded in the UUIDv7 and matches it against `start_time` in `api/v2/channels/{slug}/videos` to recover the legacy UUID, then uses that for both the metadata fetch and the yt-dlp video download. Limitation: the channel listing only returns the latest 30 VODs (no pagination), so older VODs with new-style URLs fail with an explanatory error. Legacy-UUID URLs work unchanged.
- `kick_vod_downloader.py`: a 404 from the Kick API is no longer retried 5 times with backoff — it fails (or triggers UUID resolution) immediately. Other 4xx errors (e.g. transient Cloudflare 403s on the chat API) still go through the retry loop.

## [2.4.0] - 2026-06-10

### Added

- `main.py` / `downloader.py`: new `--comments-only` flag — downloads only a video's comments (no video, subtitles, or live chat) and extracts them to `<title>_comments.csv`. The raw `.info.json` is kept alongside the CSV for debugging or re-extracting later. Mutually exclusive with `--metadata-only` and `--transcript-only`. Replaces the comments-only capability of the legacy `comments.py` (removed in 2.3.0, broken; the standalone original remains at `ytdownload/comments.py`).

## [2.3.0] - 2026-06-10

### Added

- `main.py`: auto-detect Kick VOD URLs (`kick.com/username/videos/UUID`) and route them transparently to `kick_vod_downloader.py`. VOD options (`--video-only`, `--chat-only`, `--chat-delay`) are now available in `main.py` for Kick VODs alongside existing YouTube and Kick live stream support.

### Security

- `downloader.py`: removed `nocheckcertificate: True` — TLS certificate verification is now enabled for all yt-dlp traffic. No documented reason existed for disabling it.
- `downloader.py`: switched `remote_components` from `ejs:npm` to `ejs:github`, the source yt-dlp itself recommends, reducing supply-chain exposure of the remotely fetched JS challenge solver.
- `kick_live_downloader.py`: the printed ffmpeg command no longer includes the `-headers` value, which contained live Kick session cookies; it is shown as `<redacted>`.
- `firefox_cookie_export.py`: `cookies.txt` is now created with `0600` permissions since it contains plaintext session cookies.
- `main.py`, `kick_vod_downloader.py`: yt-dlp subprocess calls now pass `--` before the URL so a URL-shaped argument starting with `-` cannot be parsed as a yt-dlp option (e.g. `--exec`).
- `requirements.txt` (app and repo root): added minimum-version pins and the missing `playwright` dependency (with a note that `playwright install firefox` is also required).

### Fixed

- `kick_live_downloader.py`: the ffmpeg `-headers` value used literal `\r\n` text (escaped backslashes) instead of real CRLF characters, so the User-Agent/Referer/Cookie headers were sent mangled.
- `add_vod_offset.py`: no longer crashes with `NameError` on a header-only (empty) CSV.
- `filter_chat.py`: no longer crashes on rows with a blank `vod_offset` (which `kick_vod_downloader.py` writes when a timestamp is unparseable). Such rows keep the emote-only and internal-repetition filters but skip the time-window filters.
- `kick_vod_downloader.py`: `fetch_with_retry` now raises an error after exhausting retries on repeated 429 responses instead of silently returning an empty result.
- `livechat_to_csv.py`: timestamps are now rendered in UTC (matching the Kick chat CSV) instead of local time.

### Removed

- `comments.py`: legacy module, unused by `main.py` and broken (called `.strftime()` on a string, returned `None` where a filename was expected).

## [2.2.2] - 2026-05-13

### Fixed

- `downloader.py`: support English subtitle variants (`en-US`, `en-GB`, `en-AU`) in addition to `en`. YouTube returns locale-specific subtitle codes, so the downloader now tries multiple variants to improve transcript compatibility across videos.

## [2.2.1] - 2026-03-30

### Fixed

- `kick_live_downloader.py`: `--use-profile` now extracts Firefox cookies via `browser_cookie3` instead of `launch_persistent_context`, which fails on macOS due to GPU Helper / XPC entitlement restrictions. Cookies are injected into a regular headless context via `add_cookies`.
- `kick_live_downloader.py`: Firefox cookie `expires` values returned by `browser_cookie3` in milliseconds (values `> 32503680000`) are now divided by 1000 before passing to Playwright, which expects seconds.
- `kick_live_downloader.py`: added `-movflags +frag_keyframe+empty_moov` to the ffmpeg command so the output MP4 is playable even if the download is interrupted mid-stream (previously the moov atom was never written on Ctrl+C).
- `kick_live_downloader.py`: switched ffmpeg audio from `-c copy` to `-c:a aac` (re-encode) to fix audio/video sync. HLS segment timestamp discontinuities cause drift when audio is stream-copied; re-encoding forces ffmpeg to resync presentation timestamps. Video is still copied (`-c:v copy`). `-bsf:a aac_adtstoasc` removed (only needed for stream copy). `-avoid_negative_ts make_zero` retained.
- `kick_live_downloader.py`: output is now saved to a new `kick_outputN/` folder (matching `kick_vod_downloader.py` behaviour). If `--out` includes a directory path the folder creation is skipped.

## [2.2.0] - 2026-03-30

### Added

- `filter_chat.py`: standalone CLI to filter noise from Kick VOD chat CSVs. Applies four passes in order: (1) emote-only removal — messages whose entire content is `[emote:ID:name]` tokens; (2) internal repetition removal — messages where the same 5-word sequence appears 3+ times (copy-paste spam); (3) per-user dedup — suppresses identical messages from the same user within a rolling time window (default: 120 s); (4) reaction flood suppression — short messages (default: ≤ 15 chars) seen more than N times (default: 5) within a sliding window (default: 30 s) are dropped. All thresholds are configurable via flags. Prints a per-filter breakdown on completion. Output written to `<input>_filtered.csv`; original is not modified.

## [2.1.2] - 2026-03-27

### Fixed

- `vtt_to_text.py`: function never returned the output path — `main.py` always fell back to recomputing it. Now returns the path correctly.
- `comments.py`: CSV progress logging used `percentage % 10 == 0`, which never triggers for non-round comment counts. Replaced with a threshold tracker.

### Changed

- `livechat_to_csv.py`: extracted `_format_ts`, `_extract_runs_text`, and `_extract_role` helpers to eliminate duplicated logic across renderer types. Added missing `role` key to membership, system, and sticker row dicts for consistency.
- `livechat_to_csv.py`: removed dead "Moderation messages (deleted)" block — it checked `liveChatTextMessageRenderer` after that renderer was already matched and returned earlier.
- `main.py`: collapsed redundant three-branch `if transcript_only / elif metadata_only / else` into `convert_transcripts()` followed by `if not transcript_only`.
- `comments.py`: removed stale filepath comment and commented-out dead function.
- `extract_comments.py`: removed stale editor tip comment.

### Removed

- `utils.py`: unused — `convert_to_eastern` superseded by `extract_comments.py`, `get_user_input` superseded by the click CLI.
- `extract_functions.py`: unused — `extract_text_and_emoji` and `extract_timestamp` superseded by helpers in `livechat_to_csv.py`.

## [2.1.1] - 2026-03-26

### Added

- `kick_vod_downloader.py`: chat CSV now includes a `vod_offset` column (first column, formatted `H:MM:SS`) giving the playback position in the downloaded video for each message, computed as `message_timestamp − vod_start_time`.
- `add_vod_offset.py`: standalone backfill script to retroactively add the `vod_offset` column to existing Kick VOD chat CSVs downloaded before this feature was added. Reads `start_time` from `metadata.json`, computes `H:MM:SS` offset per row, writes to `<name>_with_offset.csv` (original untouched). Handles missing metadata, already-present `vod_offset`, unparseable timestamps, and logs progress every 50,000 rows.

## [2.1.0] - 2026-03-26

### Added

- `kick_vod_downloader.py`: downloads Kick.com VOD replays and full chat history (CSV + NDJSON).
  - VOD metadata (`channel_id`, `start_time`, `duration`) fetched automatically from `kick.com/api/v1/video/{uuid}`.
  - Chat fetched via time-windowed polling of `web.kick.com/api/v1/chat/{channel_id}/history` in 5-second windows.
  - Message deduplication by ID and chronological sort before output.
  - Chat exported to CSV (`timestamp`, `username`, `user_id`, `message`, `type`, `badges`, `color`, `amount`, `message_id`, `metadata`) and raw NDJSON.
  - `metadata.json` saved alongside outputs.
  - `--video-only`, `--chat-only`, and `--chat-delay` flags.
  - Auto-detection of Kick's `duration` field unit (seconds vs. milliseconds).
  - Retry logic with exponential backoff (up to 5 attempts) and `429` rate-limit handling.
  - Output written to a new `kick_outputN/` folder.
- `main.py`: Kick live stream support — detects `kick.com/username` URLs, tries yt-dlp first, and automatically falls back to `kick_live_downloader` (Playwright + ffmpeg) on failure.
- `kick_live_downloader.py`: m3u8 auto-detection via Playwright network interception — `--m3u8` is now optional; the URL is captured from the player's network traffic when omitted.
- `kick_live_downloader.download_kick_live()`: callable function so `main.py` can invoke the fallback directly without a subprocess.

### Changed

- `kick_downloader.py` renamed to `kick_live_downloader.py` to distinguish it from the new VOD downloader.

## [2.0.0] - 2026-03-04

### Added

- `--metadata-only` flag: skip video download and fetch subtitles, live chat, description, and info JSON, then convert transcripts and live chat automatically.
- `--transcript-only` flag: download subtitles only and convert to deduplicated text.
- `--comments` flag: opt-in comment downloading and CSV extraction (previously an interactive prompt).
- `--cookies` flag: opt-in Firefox cookie support (previously an interactive prompt).
- `click` added as a dependency.

### Changed

- `main.py` rewritten as a `click` CLI; URL is now a positional argument instead of an interactive prompt.
- Comments are not downloaded by default (previously prompted each run).
- `downloader.py` `comments_only` parameter replaced by `metadata_only` and `transcript_only`.
- `metadata_only` mode fetches subtitles and live chat in addition to info JSON; `transcript_only` mode fetches English subtitles only (no live chat).

### Removed

- Interactive prompt-based interface in `main.py`.
- `comments_only` parameter from `YouTubeDownloader`.

## [1.3.0] - 2026-02-09

### Added

- `timestamp_converter.py`: EST/epoch timestamp converter utility.
- FFmpeg availability check in `downloader.py` — warns the user if FFmpeg is not installed when downloading video.

## [1.2.3] - 2025-12-19

### Added

- `livechat_to_csv.py`: support for vertical livestream gift rows in live chat export.

## [1.2.2] - 2025-11-29

### Changed

- `downloader.py`: added `remote_components: ejs:npm` option to improve compatibility with yt-dlp.

## [1.2.1] - 2025-11-26

### Changed

- `downloader.py`: relaxed video format preference to `bv*+ba/best` for broader compatibility.

## [1.2.0] - 2025-11-15

### Added

- `firefox_cookie_export.py`: utility to export Firefox cookies for use with yt-dlp.
- `kick_downloader.py`: downloader support for Kick.com streams.
- `livechat_to_csv.py`: expanded live chat event type handling.

## [1.1.1] - 2025-07-30

### Changed

- `remove_dupe_lines.py`: simplified deduplication logic.
- `main.py`: minor tweak to deduplication call.

## [1.1.0] - 2025-07-01

### Added

- `remove_dupe_lines.py`: deduplicate converted transcript lines.
- `livechat_to_csv.py`: expanded CSV output with additional live chat event types.
- `extract_comments.py`: handle edge cases in comment extraction.

### Changed

- `main.py`: orchestrate VTT conversion, live chat CSV export, and comment extraction after download.

## [1.0.0] - 2025-06-20

### Added

- Initial release generated with GitHub Copilot.
- `downloader.py`: yt-dlp-based video downloader with cookie and comment support.
- `main.py`: interactive prompt interface for URL, cookies, and comment options.
- `extract_comments.py`: extract comments from `.info.json` to CSV.
- `livechat_to_csv.py`: convert live chat NDJSON files to CSV.
- `vtt_to_text.py`: convert VTT subtitle files to plain text.
- `comments.py`, `utils.py`, `extract_functions.py`: supporting utilities (latter two removed in 2.1.2).
- `requirements.txt` with initial dependencies.

## Generated by AI

*Text generated by AI.*
