# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-27

### Added

- `kick-csv-analysis.py`: VADER sentiment analysis of Kick VOD chat CSVs. It writes `<input>_sentiment.csv` with per-message scores and labels, and prints a summary: overall breakdown, sentiment over time by `vod_offset` bucket, by message type, most active users (by message count), top positive/negative users, and the most extreme messages.
- `kick-csv-analysis.py --filter none|filtered|compare`: analyse the raw CSV (default), the CSV after `filter_chat.py` (run automatically as a subprocess with its default settings), or both, printing raw vs. filtered overall and time-bucket tables. In compare mode, a Note column flags buckets (≥ 10 raw messages) where filtering changes the picture: `mood flips` (positive/negative lean reverses), `emote-heavy` (under 50% of messages kept), and `mean shifts` (mean compound moves ≥ 0.1). A legend prints under the table, and the cutoffs are `NOTE_*` constants.
- `kick-csv-analysis.py --exclude-users NAMES` (comma-separated, case-insensitive, repeatable) leaves users such as bots out of all tables, time buckets and the sentiment CSV. Every report now ends with a **Bot check** table. It flags known chat-bot accounts (`KNOWN_BOTS`) as likely bots to exclude, and users whose messages are ≥ 50% links or whose name starts or ends with "bot" as possible bots. Each row shows its status (`excluded` or a suggested `--exclude-users` command), and unknown excluded names print a warning.
- README: the `filter_chat.py` options table and the `add_vod_offset.py` "safe to re-run" note, moved from `youtube-downloader-app/README.md`.
- `vaderSentiment>=3.3.2` added to the root `requirements.txt`.

## [1.0.0] - 2026-06-30

### Added

- Initial collection of stand-alone analysis scripts moved into `youtube-study/analysis/`:
  - `analyze.py` (formerly `ytdownload/analyze.py`) — YouTube live chat CSV analysis: superchat stats, author rankings, stream duration, markdown summary output.
  - `infojson2csv.py` (formerly `ytdownload/infojson2csv.py`, v1.1.0) — Batch parse yt-dlp `.info.json` files into a single CSV.
  - `filter_chat.py` (formerly `youtube-downloader-app/src/filter_chat.py`) — Kick chat CSV noise filter: emote-only, internal repetition, per-user dedup, reaction floods.
  - `add_vod_offset.py` (formerly `youtube-downloader-app/src/add_vod_offset.py`) — Backfill `vod_offset` (H:MM:SS) column into Kick VOD chat CSVs.
  - `timestamp_converter.py` (formerly `youtube-downloader-app/src/timestamp_converter.py`) — Interactive EST ↔ Unix epoch timestamp converter.
