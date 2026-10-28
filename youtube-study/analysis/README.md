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

The original CSV is not modified.

| Option | Default | Description |
| --- | --- | --- |
| `-o / --output` | `<input>_filtered.csv` | Output file path |
| `--user-dedup-window` | `120` | Seconds before a user can repeat the same message |
| `--reaction-window` | `30` | Sliding window (seconds) for reaction flood detection |
| `--reaction-max` | `5` | Max occurrences of a short reaction per window |
| `--reaction-len` | `15` | Messages at or under this character count are treated as reactions |
| `--no-emote-filter` | — | Keep emote-only messages |
| `--no-repeat-filter` | — | Keep internally repetitive messages |

### kick-csv-analysis.py

Runs sentiment analysis on a Kick VOD chat CSV (produced by `youtube-downloader-app/src/kick_vod_downloader.py`) using [VADER](https://github.com/cjhutto/vaderSentiment), a rule-based scorer tuned for social media and chat (it handles caps, `!!!`, slang, and emoji). It reads only the `vod_offset`, `timestamp`, `username`, `message`, and `type` columns. Before scoring, each `[emote:ID:name]` tag is replaced by its name. Blank messages are not scored.

Writes `<input>_sentiment.csv`, which has those columns plus the VADER `compound`/`pos`/`neu`/`neg` scores and a `positive`/`neutral`/`negative` label. Labels use VADER's standard cutoff of compound ≥ 0.05 / ≤ −0.05 (`LABEL_THRESHOLD` in the script). Expect most chat to come out neutral: VADER doesn't know emote names or game slang, so 65–85% of messages score exactly 0. It also prints a markdown summary with:

- overall breakdown
- sentiment over time, bucketed by `vod_offset` so you can seek to mood swings in the VOD
- breakdown by message type
- most active users (sorted by how many messages each user sent, with the total user count)
- most positive and most negative users (sorted by mean compound; only users with at least `--min-msgs` messages, because a few messages give unreliable averages)
- the most extreme messages

Requires `vaderSentiment` (in the root `requirements.txt`).

```zsh
python kick-csv-analysis.py chat.csv
python kick-csv-analysis.py chat.csv -o scored.csv
python kick-csv-analysis.py chat.csv --bucket 1 --top 5 --min-msgs 10
python kick-csv-analysis.py chat.csv --filter filtered   # run filter_chat.py first
python kick-csv-analysis.py chat.csv --filter compare    # raw vs. filtered side by side
python kick-csv-analysis.py chat.csv --exclude-users BotRix,<other username>   # leave out bots
```

`--filter` chooses what gets analysed:

| Value | Analyses | Writes |
| --- | --- | --- |
| `none` (default) | the raw CSV | `<input>_sentiment.csv` |
| `filtered` | the CSV after `filter_chat.py` (default settings) | `<input>_filtered.csv`, `<input>_filtered_sentiment.csv` |
| `compare` | both, and prints raw vs. filtered overall and time-bucket tables (not the user/type/message sections) | all three files above; `-o` is not allowed |

Filtering drops emote-only messages, which VADER always scores 0. In practice this cuts the neutral share a lot, while the positive and negative counts barely move. Bursts of emotes are still a sign of how chat felt, though, so `compare` shows both views.

In `compare` mode, the time-bucket table has a **Note** column that flags the windows where filtering changes the picture. Buckets with fewer than 10 raw messages are never flagged, because a handful of messages can swing the percentages by chance.

| Note | Technical rule | In plain English |
| --- | --- | --- |
| `mood flips` | positive > negative in raw but negative > positive after filtering, or the reverse | Removing the noise changes the verdict on whether chat was happy or upset. This is rare, because the removed emote-only messages are neutral anyway. When it happens, the cause is usually one person repeating the same message. |
| `emote-heavy` | filtering keeps under 50% of the bucket's messages | More than half of chat was emote spam, like a crowd that is mostly cheering rather than talking. These are often hype or reaction moments worth jumping to in the VOD. |
| `mean shifts` | the mean compound moves by 0.1 or more | The average mood looks much stronger once the neutral noise is gone. Picture a room where a few people are shouting while most just clap: once the clapping is taken out, the shouting stands out. It flags the moments when chat was clearly happy or clearly upset. |

On an 8,000-message chat with 5-minute buckets, about 10% of buckets were `emote-heavy`, about 3% were `mean shifts`, and none were `mood flips`. The cutoffs are the `NOTE_*` constants at the top of the script.

#### Bot check and `--exclude-users`

Every report ends with a **Bot check** table listing users that look like bots, and why. In plain English: chat bots post a lot of automatic messages (follow reminders, Discord links, "X reached level 15!"), and those messages make the averages look like what the bot says rather than what people feel.

| Signal | Rule | How sure |
| --- | --- | --- |
| Known chat-bot account | name is a bot service such as BotRix, Nightbot or StreamElements (`KNOWN_BOTS`) | Likely bot. The status says it should be excluded. |
| Mostly links | at least 50% of the user's messages contain a link (minimum 5 messages) | Possible bot or spam account. Check its messages. |
| "bot" in the name | name starts or ends with "bot"/"bots" (e.g. `examplebot42`) | Weak. Could easily be a person. Check its messages. |

The check only reports; nobody is removed automatically. To leave users out, list them with `--exclude-users`: comma-separated, case-insensitive, and the flag can be repeated. Excluded users are dropped from every table, the time buckets and the `_sentiment.csv` output. They then appear in the Bot check table with status `excluded`. A name that isn't in the chat prints a warning, which catches typos. Repeated or copy-pasted messages aren't used as a bot signal, because human spammers repeat themselves just as much.

#### Walkthrough: analysing a Kick chat

A typical session goes from finding bots, to reading the cleaned chat, to finding the key moments in the VOD. Each run takes about a second, even on a chat of several MB.

**1. Set up.** Activate the venv, then work inside the `kick_outputN/` folder that `kick_vod_downloader.py` created (in the directory you ran it from). All output files then sit next to the chat, and if that folder is gitignored (as `youtube-downloader-app/src/kick_output*/` is), they can't end up in a commit. Store the script path in a variable so the commands stay short. How `$KCA` works, and why it's named that, is explained in [`_doc/programming_reference.md`](../../_doc/programming_reference.md#shortening-a-long-script-path-with-a-variable-kca).

```zsh
cd /path/to/babel_lib && . venv/bin/activate
KCA="$PWD/youtube-study/analysis/kick-csv-analysis.py"
cd youtube-downloader-app/src/kick_outputN
ls *_chat.csv     # should list exactly one file
```

Chat file names often contain spaces. If `ls` lists more than one file, use the full name in quotes instead of `*_chat.csv`; typing a few letters and pressing Tab fills it in. A note on sizes: `ls -lh` counts 1 MB as 1,048,576 bytes, while macOS Finder counts 1,000,000, so a file listed as 2.6M can appear as 2.8 MB in Finder.

**2. Check for bots.** Run the report on the filtered chat without excluding anyone, and save it to a file:

```zsh
python "$KCA" *_chat.csv --filter filtered --top 15 > report_before.md
```

Open the file in VS Code and press ⇧⌘V for the Markdown preview. Look at two sections:

- **Most active users**: a chat bot is often at or near the top.
- **Bot check** (last section): *likely* and *possible* bots, and the reason each was flagged.

**3. Read each possible bot's messages before deciding.** Being flagged doesn't make an account a bot. This prints every message from one user, with its VOD offset:

```zsh
python -c 'import csv,sys; [print(r["vod_offset"], "|", r["message"][:100].replace("\n"," ")) for r in csv.DictReader(open(sys.argv[1],encoding="utf-8")) if r["username"].lower()==sys.argv[2].lower()]' *_chat.csv <username>
```

Signs of a bot or spam account:

- the same text over and over
- links in almost every message
- posts at fixed intervals
- never replies to anyone

If it reads like someone taking part in the conversation, it's a person. This command reads the raw `_chat.csv`, not the filtered copy, because `filter_chat.py` removes repeated messages, and repetition is exactly what you're looking for here.

**4. Rerun with the bots excluded.** List the names comma-separated, with no spaces:

```zsh
python "$KCA" *_chat.csv --filter filtered --top 15 --exclude-users BotRix,<username> > report_after.md
```

In `report_after.md`, check that:

- the **Bot check** table shows the excluded users as `excluded` (a typo prints a "no such user" warning)
- they're gone from **Most active users**
- the **Messages** and **Mean compound** lines at the top have changed from `report_before.md`, which shows how much the bots were affecting the averages

This report is the main result. It covers sentiment over time, by message type, the most active, positive and negative users, and the most extreme messages with their VOD offsets.

**5. Find the key moments.** Compare the raw and filtered timelines, with the same exclusions:

```zsh
python "$KCA" *_chat.csv --filter compare --exclude-users BotRix,<username> > compare_report.md
```

In the **Note** column, runs of `emote-heavy` usually mark moments where chat erupted, and `mean shifts` mark moments where chat was clearly happy or clearly upset. Note those `VOD offset` times and jump to them in the video.

**Optional changes** (add them to any command above):

| Want | Add |
| --- | --- |
| A finer timeline, to look closely at one moment | `--bucket 1` |
| A wider overview of a long stream | `--bucket 30` |
| Rank only regular chatters | `--min-msgs 20` |
| Longer top-user and message lists | `--top 25` |

**Files in the folder afterwards:**

- `…_chat_filtered.csv`: the cleaned chat
- `…_chat_sentiment.csv` and `…_chat_filtered_sentiment.csv`: one row per message, with scores
- your `.md` reports

Each run overwrites the CSVs from the previous run, but the reports are kept because you give each one its own name. Before opening any of these CSVs in a spreadsheet, read "Opening chat CSVs safely" in the youtube-downloader-app README. Chat messages can contain text that Excel would run as a formula.

### add_vod_offset.py

Backfills a `vod_offset` column (H:MM:SS) into an existing Kick VOD chat CSV (produced by `youtube-downloader-app/src/kick_vod_downloader.py`). The offset is the playback position in the video for each message, calculated from `message_timestamp − vod_start_time`. Useful for seeking to a specific chat message in VLC or a video editor.

Looks for a `metadata.json` in the same folder as the CSV if not specified. Output is written to `<original>_with_offset.csv`.

```zsh
python add_vod_offset.py chat.csv
python add_vod_offset.py chat.csv metadata.json
```

The original CSV is not modified. If it already has a `vod_offset` column, that column is dropped and recalculated, so the script is safe to run more than once.

### timestamp_converter.py

Interactive EST ↔ Unix epoch timestamp converter. Useful when cross-referencing timestamps in chat CSVs (produced by `ytdownload/livechat.py` or `youtube-downloader-app`) with video timecodes. Accepts 24-hour time (`HHMM`) or date+time (`YYYYMMDD-HHMM`) and converts in both directions.

```zsh
python timestamp_converter.py
```
