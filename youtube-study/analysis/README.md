# README

Stand-alone analysis scripts for files produced by `youtube-downloader-app` and `ytdownload`. Run each script directly from this folder or any working directory.

## Scripts

### analyze.py

Analyzes a YouTube live chat CSV (produced by `ytdownload/livechat.py`). Reports superchat count, total superchat value by currency, per-author message counts, and stream duration. Outputs a markdown summary table and writes an `analyze.log` file.

```zsh
python analyze.py
# prompts: Live chat CSV filename?
```

### infojson2csv.py

Parses one or more yt-dlp `.info.json` metadata files (produced by `youtube-downloader-app` or `ytdownload/download.py` with `--metadata-only`) into a single CSV, one row per video.

```zsh
python infojson2csv.py                            # current directory
python infojson2csv.py path/to/dir                # specific directory
python infojson2csv.py path/to/dir -o out.csv     # custom output file
python infojson2csv.py path/to/dir --no-markdown  # skip markdown summary
```

### filter_chat.py

Cleans up a Kick VOD chat CSV (produced by `youtube-downloader-app/src/kick_vod_downloader.py` or `youtube-downloader-app/src/main.py` for Kick VOD URLs) by removing noise. Filters applied in order:

1. **Emote-only** — messages made up entirely of `[emote:ID:name]` tags.
2. **Internal repetition** — messages where the same phrase is copy-pasted multiple times.
3. **Per-user dedup** — repeated identical messages from the same user within a rolling time window.
4. **Reaction floods** — bursts of the same short reaction from a single user.

Output is written to `<input>_filtered.csv` by default.

```zsh
python filter_chat.py chat.csv
python filter_chat.py chat.csv -o cleaned.csv
```

### add_vod_offset.py

Backfills a `vod_offset` column (H:MM:SS) into an existing Kick VOD chat CSV (produced by `youtube-downloader-app/src/kick_vod_downloader.py`). The offset is the playback position in the video for each message, calculated from `message_timestamp − vod_start_time`. Useful for seeking to a specific chat message in VLC or a video editor.

Looks for a `metadata.json` in the same folder as the CSV if not specified. Output is written to `<original>_with_offset.csv`.

```zsh
python add_vod_offset.py chat.csv
python add_vod_offset.py chat.csv metadata.json
```

### timestamp_converter.py

Interactive EST ↔ Unix epoch timestamp converter. Useful when cross-referencing timestamps in chat CSVs (produced by `ytdownload/livechat.py` or `youtube-downloader-app`) with video timecodes. Accepts 24-hour time (`HHMM`) or date+time (`YYYYMMDD-HHMM`) and converts in both directions.

```zsh
python timestamp_converter.py
```
