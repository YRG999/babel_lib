# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## General Rules

- When asked to explore or fix something, always check existing project code and files first before suggesting external tools or new approaches.

## Repository Overview

A collection of experimental Python scripts and utilities. The two most actively developed areas are the YouTube/Kick downloaders. The repo uses a single shared virtualenv at the root.

## Setup

```zsh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

After initial setup, only `. venv/bin/activate` is needed to reactivate.

External tools required by various scripts:
- `yt-dlp` — included in `requirements.txt`
- `ffmpeg` — `brew install ffmpeg` (required for video merging and `captions.py`)
- `playwright` — Kick live stream fallback in `youtube-downloader-app`

## Running Scripts

Most scripts are run directly from their subdirectory:

```zsh
# Modern YouTube/Kick downloader
python youtube-downloader-app/src/main.py "URL"

# Live chat capture (prompts for video URL/ID)
python ytdownload/livechat.py

# Real-time transcription (Apple Silicon only)
python ytdownload/captions.py

# Directory comparison/sync
bash dir_compare/dir_compare.sh <source> <dest> [--dry-run | --compare]
```

**Always quote YouTube URLs in zsh** — `?` in `?v=...` is a glob wildcard.

## Key Submodules

### `youtube-downloader-app/` — Primary downloader (see its own CLAUDE.md)
- Entry point: `src/main.py` (click CLI)
- Downloads YouTube video/metadata/transcripts/live chat and Kick VODs/live streams
- Output folders: `outputN/` for YouTube, `kick_outputN/` for Kick

### `ytdownload/` — Live-stream-focused tools (see its own CLAUDE.md)
- Entry point: `livechat.py` — real-time YouTube live chat via YouTube Data API v3
- `captions.py` — real-time transcription (mlx-whisper, Apple Silicon GPU only); run simultaneously with `livechat.py` in a separate terminal
- API key in `.env` as `YOUTUBE_API_KEY`; quota tracked in `.youtube_quota.json` (10,000 units/day)

### `dir_compare/dir_compare.sh` — Directory sync utility
- Copies files from source that are missing in destination
- `--dry-run`: preview only; `--compare`: show missing files in both directions, writes timestamped report

### `browser_history/` — Chrome history SQLite tools
- Scripts to extract and export Chrome browsing history from the `History` SQLite DB to CSV

### Standalone scripts
- `encodeDecodeImage/` — LSB steganography (Pillow)
- `games/` — Dice/probability games
- `wordplay/` — Word/sentence generation using `random-word-api.herokuapp.com`
- `other/` — Misc calculators, scrapers, and visualizers
- `radius/radius.py` — Google Maps geocoding + folium radius map

## Configuration

- **`.env`** — `YOUTUBE_API_KEY`, `MAPS_API_KEY` (create at repo root or in `ytdownload/`)
- **`requirements.txt`** — Shared across all submodules

## Documentation

- `_doc/programming_notes.md` — Dated troubleshooting log (problem/cause/fix)
- `_doc/programming_reference.md` — API links and how-to reference
- `_doc/README.md` — Full index of docs and session summaries

## After Every Change

After any code change, update all related documentation as applicable: `CHANGELOG.md`, `README.md`, `CLAUDE.md`, and the session summary file.

## Development Environment

- **Shell:** macOS with bash 3.2. Avoid bash 4+ features — no associative arrays, no empty array expansion with `set -u`, etc.

## Session Summaries

At the end of each session, add a summary of what was done to `_doc/claude_summaries/chat-summary_YYYY-MM-DD.md` using today's date. If a file for today already exists, append a new numbered section to it. If not, create it. Only include what is unique to the session — do not duplicate content already covered in a summary for the same date.
