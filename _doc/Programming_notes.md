# Programming notes

*Troubleshooting log — add new entries here when you encounter and solve a specific problem. Include: date, problem, cause, fix, and references. For reference tables, API links, and conceptual notes organized by topic, use [programming_reference.md](programming_reference.md).*

- [Claude Code custom skills: project vs user level](#claude-code-custom-skills-project-vs-user-level)
- [Claude Code skills: simplify, loop, schedule, and more](#claude-code-skills-simplify-loop-schedule-and-more)
- [kick_vod_downloader.py: FixupM3u8 failure and missing chat](#kick_vod_downloaderpy-fixupm3u8-failure-and-missing-chat)
- [ytdownload docs reorganization and changelog reconstruction](#ytdownload-docs-reorganization-and-changelog-reconstruction)
- [VSCode Python terminal activating twice](#vscode-python-terminal-activating-twice)
- [Updated yt-dlp to download videos](#updated-yt-dlp-to-download-videos)
- [Download kick videos](#download-kick-videos)
- [Couldn't solve JS challenge](#couldnt-solve-js-challenge)
- [Markdownlint bullets `*` or `-`](#markdownlint-bullets--or--)
- [Python venv hung](#python-venv-hung)
- [VS Code black screen UI](#vs-code-black-screen-ui)
- [Update GitHub CLI passphrase & add once](#update-github-cli-passphrase--add-once)
- [yt-dlp downloading audio-only webm](#yt-dlp-downloading-audio-only-webm)

## Claude Code custom skills: project vs user level

- *Sat, Apr 4, 2026*

Custom skills are slash commands you define yourself. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown instructions.

### Project vs user level

| Level | Path | Applies to |
| --- | --- | --- |
| User | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |

**Use user-level** for skills that apply everywhere — session summaries, personal workflows, general-purpose helpers.

**Use project-level** for skills tied to a specific repo — deploy scripts, project-specific conventions, team workflows (commit to version control so the whole team gets them).

### SKILL.md format

```yaml
---
name: skill-name
description: What it does and when Claude should use it
---

Instructions here...
```

All frontmatter fields are optional, but `description` is recommended — Claude uses it to decide when to invoke the skill automatically. Without `disable-model-invocation: true`, Claude can also trigger it on its own when relevant.

### Creating a skill (VS Code)

```zsh
mkdir -p ~/.claude/skills/my-skill
# create ~/.claude/skills/my-skill/SKILL.md with frontmatter + instructions
```

Quit and restart VS Code after creating a new skill — the VS Code extension does not pick up new skills via live reload.

### Documentation

Full reference: <https://code.claude.com/docs/en/slash-commands>

### Asking Claude to suggest skills for a project

```txt
Analyze this project and suggest custom skills that would be useful. Consider what tasks I do repeatedly, what conventions are specific to this repo, and what workflows could be automated.
```

Or to run the interactive setup flow (requires `CLAUDE_CODE_NEW_INIT=1` in environment):

```zsh
CLAUDE_CODE_NEW_INIT=1 claude
# then run /init
```

This walks through skills and hooks interactively before writing anything.

---

## Claude Code skills: simplify, loop, schedule, and more

- *Sat, Mar 28, 2026*

Claude Code skills are slash commands that expand into full prompts for common tasks. Invoke them by typing `/skill-name` in the Claude Code chat input.

### `/simplify`

Reviews recently changed code for quality, redundancy, and efficiency, then fixes any issues found. Works on whatever was last edited. To target a specific file, just ask directly:

```txt
Simplify and clean up src/main.py
```

### `/update-config`

Configures Claude Code behavior via `settings.json` using plain English. Use it to set up automated hooks (actions that run before/after tool calls), set permissions, or define environment variables:

```txt
/update-config allow running ffmpeg commands without asking
/update-config whenever I finish editing a python file, remind me to test it manually
/update-config set PYTHONPATH=src
```

### `/loop`

Runs a prompt on a recurring interval. Useful for polling long-running processes or monitoring output:

```txt
/loop 5m check if any new output folders were created
```

Defaults to 10 minutes if no interval is given.

### `/schedule`

Creates a scheduled remote agent that runs on a cron schedule — for automating tasks that should repeat over time, not just for the current session.

### `/keybindings-help`

Customize keyboard shortcuts in `~/.claude/keybindings.json`. Use when you want to rebind keys, add chord shortcuts, or change the submit key.

### `/claude-api`

Scaffolds or assists with apps built using the Anthropic SDK or Claude Agent SDK. Triggered automatically when code imports `anthropic` or `@anthropic-ai/sdk`.

---

## kick_vod_downloader.py: FixupM3u8 failure and missing chat

- *Sat, Mar 28, 2026*

### Problem

`kick_vod_downloader.py` downloaded the video successfully (100%) but failed during post-processing:

```txt
[FixupM3u8] Fixing MPEG-TS in MP4 container of "VIDEO.mp4"
ERROR: Postprocessing: Conversion failed!
Error: yt-dlp failed (see output above).
```

Chat was also not downloaded.

### Cause

Two separate issues:

1. **FixupM3u8 failure** — FFmpeg was not installed. The `FixupM3u8` post-processor requires FFmpeg to remux the HLS MPEG-TS stream into a proper MP4 container after download.
2. **Chat not downloaded** — The script raises an exception when yt-dlp exits with a non-zero code ([kick_vod_downloader.py:254-255](../youtube-downloader-app/src/kick_vod_downloader.py#L254-L255)), exiting before it reaches the chat download step.

### Fix

Install FFmpeg:

```zsh
brew install ffmpeg
```

To get the chat without re-downloading the video, use `--chat-only`:

```zsh
python src/kick_vod_downloader.py --chat-only "KICK_VOD_URL"
```

To fix the already-downloaded video without re-downloading, remux directly with FFmpeg:

```zsh
ffmpeg -i "VIDEO.mp4" -c copy "VIDEO_fixed.mp4"
```

Note: yt-dlp does **not** automatically skip re-downloading after a post-processing failure — running it again will restart the download. Use the FFmpeg remux approach instead.

### What FFmpeg does during remux

The downloaded `.mp4` file is actually an MPEG-TS transport stream with the wrong extension — ffmpeg detects this automatically (`Input #0, mpegts`). With `-c copy` it reads the TS container and rewrites the streams into a proper MP4 container with no re-encoding and no quality loss.

The input has three streams; only two are mapped to the output:

| Stream | Codec | Details | Output |
| --- | --- | --- | --- |
| Video | H.264 High | 1920×1080, 60fps | Mapped (stream 0) |
| Audio | AAC LC | 48kHz stereo | Mapped (stream 1) |
| Data | timed_id3 | HLS metadata | Dropped |

Performance is fast — ~924× real-time on Apple Silicon. An 18h39m VOD remuxed in 1m12s. Muxing overhead is ~0.18%, so output file size is essentially identical to input.

### Disk space

Large VODs (65+ GiB) can fill the disk, causing errors like `ENOSPC: no space left on device` in unrelated tools. Check usage with:

```zsh
df -h
du -sh ~/* 2>/dev/null | sort -rh | head -20
```

To avoid filling the disk, download to an external drive by `cd`-ing there before running the script, or pass an explicit output path.

## ytdownload docs reorganization and changelog reconstruction

- *Mon, Mar 9, 2026*

Reorganized all documentation in `ytdownload/` and reconstructed a full version history for `livechat.py`.

### New tool: `csv_to_livechat.py`

Created to convert a `livechat.py` CSV export to yt-dlp `.live_chat.json` format for replay in [mpv-youtube-chat](https://github.com/BanchouBoo/mpv-youtube-chat). Key problem: `livechat.py` saves wall-clock Eastern Time timestamps; `.live_chat.json` requires millisecond offsets from stream start (`videoOffsetTimeMsec`).

Start time detection waterfall:

1. `--start` flag (Unix timestamp or date string)
2. `INFO.json` positional arg (`release_timestamp` field)
3. `--video` flag: reads `creation_time` via ffprobe, compares to first chat message, recommends which to use
4. Interactive prompt

Recommendation logic for `--video` mode:

- Gap 0–600s: video `creation_time` is likely the live download start → recommended
- First chat is earlier than video: stream was already live when downloaded → first chat recommended
- Gap > 600s: suspiciously large offset → first chat recommended as conservative estimate

### Changelog extraction

Extracted embedded changelogs from `README_livechat.md` and `README_livecaptions.md` into standalone files:

- `CHANGELOG_livechat.md`
- `CHANGELOG_captions.md` (renamed from `CHANGELOG_livecaptions.md` to match the `livecaptions.py` → `captions.py` rename)

### Changelog reconstruction for `livechat.py`

Rebuilt a full 19-version history from two sources:

- **git log**: `git log --follow --diff-filter=R` and `git show HASH:file | head` to identify which versions were committed and on what dates
- **`_notes/youtube/live-chat-fetch/`**: 14 archived files (v1–v13) with `ls -lT` for file modification timestamps

**Key finding**: The script was in the repository as far back as 2024-08-11 (commit `1523731`) as `youtubedl/youtube-live-chat-fetcher.py`, not 2025-01-21 as originally thought. It passed through multiple filenames before becoming `livechat.py`:

| Filename | First git commit |
| --- | --- |
| `youtubedl/youtube-live-chat-fetcher.py` | 2024-08-11 |
| `ytdownload/youtube-live-chat-fetcher.py` | 2024-08-24 |
| `ytdownload/youtube_live_chat_fetcher.py` | 2024-09-08 |
| `ytdownload/youtube_live_chat_fetcher14.py` | 2024-09-15 |
| `ytdownload/livechat.py` | 2025-01-21 |

### Proper SemVer renumbering

All 19 historic versions (originally numbered v1–v16) were renumbered using semantic versioning. Final range: 1.0.0–3.3.0. Each entry notes the historic version number.

Major version bumps:

- **2.0.0** (historic v2): breaking — auth method changed from OAuth to API key, requiring new `.env` config
- **3.0.0** (historic v15): `QuotaManager` introduces cross-session persistent state file (`.youtube_quota.json`), fundamentally changing the behavior model between runs

The rename to `livechat.py` was split into its own entry (2.12.0) as a minor version.

### Documentation files changed

| File | Action |
| --- | --- |
| `csv_to_livechat.py` | Created |
| `README_csv_to_livechat.md` | Created |
| `CHANGELOG_csv_to_livechat.md` | Created |
| `CHANGELOG_livechat.md` | Created (extracted from README, reconstructed) |
| `CHANGELOG_captions.md` | Renamed from `CHANGELOG_livecaptions.md` |
| `README_captions.md` | Renamed from `README_livecaptions.md`, updated references |
| `README_livechat.md` | Removed embedded changelog, added link |
| `README.md` | Added Related Documentation table linking all READMEs and CHANGELOGs |

### README.md clarifications and cleanup

- Clarified in the Core Tools table that `livechat.py` does not do transcription and that `captions.py` is run separately from `livechat.py` — these are independent parallel tools
- Converted all 8 tables in `README.md` from padded/aligned style to markdownlint compact style (`| --- |` separators, no column padding)

### Marking untested code

`csv_to_livechat.py` was written but never run. Best practice for untested code:

1. **In the source file** — add a comment in the header: `# NOTE: This script has not been tested. Use with caution.`
2. **In the changelog** — add an `[Unreleased]` section at the top (the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention) with a note that the code is untested

When the code has been tested and works, remove the header comment, drop the `[Unreleased]` section, and commit.

### Debugging `captions.py`

Several bugs found while running live:

| Error | Cause | Fix |
| --- | --- | --- |
| "Requested format is not available" | `bestaudio` format not available for live streams | Change format selector to `bestaudio/best` |
| HuggingFace 401 "Repository Not Found" | Model names in `model_map` missing `-mlx` suffix | Add `-mlx` to all entries (e.g. `whisper-base-mlx`) |
| IDE error on `result.get` | `import mlx_whisper` is lazy (inside function), so type checker can't infer return type | Add `result: dict =` annotation |
| Transcript duplication (phrases repeated 10+ times) | Whisper hallucinating during silence with default `condition_on_previous_text=True` | Set `condition_on_previous_text=False` + filter segments where `no_speech_prob >= 0.6` |
| "to to to to to" × 50, repetitive nonsense | Hallucinations not caught by `no_speech_prob` — Whisper was confident but pattern-matching noise | Add `compression_ratio < 2.4` per-segment filter (repetitive text compresses extremely well) |
| "DON DON DON..." × 200 | Short segments bypass `compression_ratio` filter — zlib overhead prevents ratio from exceeding 2.4 for short strings | Add regex filter: discard segments where any word repeats 4+ times consecutively (`\b(\w+)\b(?:\s+\1){3,}`) |
| Timestamps ~1 minute in the future | ffmpeg downloads buffered YouTube CDN audio faster than real-time, so `chunk_index * chunk_duration` accumulated ahead of wall clock | Record `chunk_capture_start = datetime.now()` immediately before each ffmpeg call; use that as the chunk timestamp |

### Silence markers in `captions.py`

Added silence markers to the CSV output: after 5 minutes with no transcribed speech, writes a `[silence]` row (with current timestamp, empty Start/End). Resets each time speech or a silence marker is written, so markers appear every 5 minutes throughout a long silent period. Implemented entirely in the main transcription loop — no changes to the audio thread.

### Keep a Changelog: `### Added` vs `### Fixed`

Silence markers are a new feature, not a bug fix. In [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format, a single version entry can have multiple subsections (`### Added`, `### Changed`, `### Fixed`, etc.). Split them when a version contains both new features and bug fixes.

## VSCode Python terminal activating twice

- *Thu, Feb 26, 2026*

### Problem

When opening a new VSCode terminal, `source .../venv/bin/activate` was running twice instead of once.

### Cause

Two extensions were both activating the environment independently:

- **`ms-python.python`** (main Python extension) — activates via `python.terminal.activateEnvironment: true`
- **`ms-python.vscode-python-envs`** (new Python Environments extension, GA Feb 2026) — activates via `python-envs.terminal.autoActivationType: "command"` (its default)

Neither extension checks whether the other has already activated, so both fire on every new terminal.

### Background

`vscode-python-envs` is Microsoft's new dedicated environment manager, designed to support the broader ecosystem (venv, conda, uv, hatch, pixi, etc.) with a unified UI and plugin API. It hit general availability in February 2026 after a year in preview. It is intended to eventually supersede the environment management parts of the main Python extension, including deprecating `python.terminal.activateEnvironment`.

### Fix (forward-looking approach)

Disable the legacy setting and use the new extension's `shellStartup` mode, which is Microsoft's recommended future default (activates before the first prompt, integrates better with Copilot terminal):

```json
"python.terminal.activateEnvironment": false,
"python-envs.terminal.autoActivationType": "shellStartup"
```

`shellStartup` activates silently before the first prompt appears. `command` (the current default) runs the activation command visibly after the terminal opens.

### References

- [Terminal Auto-Activation Explained (Microsoft Wiki)](https://github.com/microsoft/vscode-python-environments/wiki/Terminal-Auto%E2%80%90Activation-Explained)
- [Settings Review: Python ext & Python Envs ext — Issue #861](https://github.com/microsoft/vscode-python-environments/issues/861)
- [Activation ignored when python.terminal.activateEnvironment is disabled — Issue #602](https://github.com/microsoft/vscode-python-environments/issues/602)
- [Python Environments Extension for VS Code — Feb 2026 release announcement](https://devblogs.microsoft.com/python/python-in-visual-studio-code-february-2026-release/)
- [Dedicated Python Environments Tool Rolls Out — Visual Studio Magazine](https://visualstudiomagazine.com/articles/2025/08/18/dedicated-python-environments-tool-rolls-out-in-vs-code-update.aspx)

## Updated yt-dlp to download videos

- *Thu, Nov 27, 2025*

### Background

yt-dlp requires an external JS runtime (Deno or Node) for full YouTube support, including solving JS challenges.

### Problem

After installing Deno and Node, yt-dlp was still only downloading `.m4a` audio, not `.mp4` video. Video files weren't appearing at all.

### Fix

Install the yt-dlp EJS Python package:

```zsh
pip install -U "yt-dlp[default]"
```

### References

- [[Announcement] External JavaScript runtime now required for full YouTube support #15012](https://github.com/yt-dlp/yt-dlp/issues/15012)
- [Deno](https://deno.com/)
- [Deno on GitHub](https://github.com/denoland/deno/)
- [yt-dlp EJS wiki](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [Node.js](https://nodejs.org/en)

## Download kick videos

### Problem

```txt
yt-dlp https://kick.com/user/videos/12345
[kick:vod] Extracting URL: https://kick.com/user/videos/12345
[kick:vod] 12345: Downloading API JSON
WARNING: [kick:vod] The extractor is attempting impersonation, but no impersonate target is available.
ERROR: [kick:vod] 12345: Unable to download JSON metadata: HTTP Error 403: Forbidden
```

### Fix

```zsh
pip install "yt-dlp[default,curl-cffi]"
```

To download, enter the video URL from the address bar, same as YouTube:

```zsh
kick VIDEO_URL
```

### References

- [yt-dlp impersonation docs](https://github.com/yt-dlp/yt-dlp#impersonation)

## Couldn't solve JS challenge

### Problem

```zsh
(venv) user@hostname babel_lib % yt-dlp --cookies-from-browser firefox -v -F "https://www.youtube.com/watch?v=VIDEO_ID"
[debug] Command-line config: ['--cookies-from-browser', 'firefox', '-v', '-F', 'https://www.youtube.com/watch?v=VIDEO_ID']
[debug] Encodings: locale UTF-8, fs utf-8, pref UTF-8, out utf-8, error utf-8, screen utf-8
[debug] yt-dlp version stable@2025.11.12 from yt-dlp/yt-dlp [335653be8] (pip)
[debug] Python 3.14.0 (CPython arm64 64bit) - macOS-26.1-arm64-arm-64bit-Mach-O (OpenSSL 3.6.0 1 Oct 2025)
[debug] exe versions: ffmpeg 8.0 (setts), ffprobe 8.0
[debug] Optional libraries: Cryptodome-3.23.0, brotli-1.2.0, certifi-2025.11.12, mutagen-1.47.0, requests-2.32.5, sqlite3-3.51.0, urllib3-2.5.0, websockets-15.0.1
[debug] JS runtimes: deno-2.5.6
[debug] Proxy map: {}
Extracting cookies from firefox
[debug] Extracting cookies from: "/Users/username/Library/Application Support/Firefox/Profiles/PROFILE-ID.default-release/cookies.sqlite"
[debug] Firefox cookies database version: 16
Extracted 63 cookies from firefox
[debug] Request Handlers: urllib, requests, websockets
[debug] Plugin directories: none
[debug] Loaded 1844 extractors
[debug] [youtube] Found YouTube account cookies
[debug] [youtube] [pot] PO Token Providers: none
[debug] [youtube] [pot] PO Token Cache Providers: memory
[debug] [youtube] [pot] PO Token Cache Spec Providers: webpo
[debug] [youtube] [jsc] JS Challenge Providers: bun (unavailable), deno, node (unavailable), quickjs (unavailable)
[youtube] Extracting URL: https://www.youtube.com/watch?v=VIDEO_ID
[youtube] VIDEO_ID: Downloading webpage
[debug] [youtube] Detected YouTube Premium subscription
[debug] [youtube] Forcing "main" player JS variant for player 89e685a2
original url = /s/player/89e685a2/player_es6.vflset/en_US/base.js
[youtube] VIDEO_ID: Downloading tv downgraded player API JSON
[youtube] VIDEO_ID: Downloading web creator player API JSON
[youtube] VIDEO_ID: Downloading player 89e685a2-main
[youtube] [jsc:deno] Solving JS challenges using deno
[debug] [youtube] [jsc:deno] Checking if npm packages are cached
[debug] [youtube] [jsc:deno] Running deno: deno run --ext=js --no-code-cache --no-prompt --no-remote --no-lock --node-modules-dir=none --no-config --cached-only -
WARNING: [youtube] [jsc] Remote components challenge solver script (deno) and NPM package (deno) were skipped. These may be required to solve JS challenges. You can enable these downloads with --remote-components ejs:github (recommended) or --remote-components ejs:npm , respectively. For more information and alternatives, refer to https://github.com/yt-dlp/yt-dlp/wiki/EJS
WARNING: [youtube] VIDEO_ID: Signature solving failed: Some formats may be missing.
WARNING: [youtube] VIDEO_ID: n challenge solving failed: Some formats may be missing.
WARNING: Only images are available for download. use --list-formats to see them
[info] Available formats for VIDEO_ID:
ID EXT RESOLUTION FPS │ PROTO │ VCODEC MORE INFO
────────────────────────────────────────────────────
sb3 mhtml 48x27 0 │ mhtml │ images storyboard
sb2 mhtml 80x45 0 │ mhtml │ images storyboard
sb1 mhtml 160x90 0 │ mhtml │ images storyboard
sb0 mhtml 320x180 0 │ mhtml │ images storyboard
```

### Fix

Add `'remote_components': 'ejs:npm',` to `ydl_opts` in `download_video_info_comments` in [downloader.py](../youtube-downloader-app/src/downloader.py).

Current `downloader.py` setup:

- Lets yt-dlp choose the best formats (no explicit `format`)
- Enables EJS solving via `remote_components='ejs:npm'`
- Uses browser cookies when `use_cookies=True`
- Muxes output to MP4 when possible via `merge_output_format='mp4'`

To debug a failing URL directly in the terminal:

```zsh
yt-dlp --cookies-from-browser firefox --remote-components ejs:npm -F "URL"
```

## Markdownlint bullets `*` or `-`

### Question

Why does markdownlint recommend asterisks for unordered bullets sometimes and hyphens other times?

### Answer

The relevant rule is **MD004 – Unordered list style**, which controls whether you use `-`, `*`, `+`, or a "consistent" style. Config options:

- `"dash"` → always use `-`
- `"asterisk"` → always use `*`
- `"plus"` → always use `+`
- `"consistent"` → whatever the first bullet in the file or list is, all others must match

The default for MD004 is `"consistent"`, defined in the markdownlint rule docs.

### References

- [MD004 rule docs](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md#md004)

## Python venv hung

### Problem

`python -V` hung with no output.

### Fix

Remove and reinstall the virtual environment:

```zsh
which python3
python3 -V
cd /Users/username/Repos/babel_lib
rm -rf venv
python3 -m venv venv
. venv/bin/activate
python -V
pip install -r requirements.txt
```

## VS Code black screen UI

- *Tue, Jan 6, 2026*
- [Related GitHub issue #282662](https://github.com/microsoft/vscode/issues/282662)

### Problem

VS Code UI turns black after running for over a day without restarting. This is a GPU/hardware acceleration issue in Electron that appears after long uptimes.

### Fix

**If terminals must stay running — reload without closing VS Code:**

Use the Command Palette even if the UI is black:

1. Press `Cmd`+`Shift`+`P`
2. Type `Reload Window` and press `Enter`

Terminal processes reconnect after the reload. Note: tabs are preserved but virtual environments need to be re-activated manually.

**Permanent fix (requires full restart):**

1. Press `Cmd`+`Shift`+`P`
2. Type `Preferences: Configure Runtime Arguments` and select it
3. In `argv.json`, add:

   ```json
   {
     "disable-hardware-acceleration": true
   }
   ```

4. Save and fully restart VS Code.

## Update GitHub CLI passphrase & add once

### Update SSH key passphrase

Change the passphrase on an existing key without regenerating it:

```zsh
ssh-keygen -p -f ~/.ssh/id_ed25519
```

Replace `id_ed25519` with your actual key filename if different.

### Enter passphrase only once

Add your SSH key to `ssh-agent` to cache the passphrase for the session.

#### macOS

1. **Start the ssh-agent**:

   ```zsh
   eval "$(ssh-agent -s)"
   ```

2. **Configure automatic loading** — edit or create `~/.ssh/config`:

   ```zsh
   touch ~/.ssh/config
   ```

   (`touch` produces no output on success. Verify with `ls -la ~/.ssh/config`.)

   Add these lines:

   ```txt
   Host github.com
     AddKeysToAgent yes
     UseKeychain yes
     IdentityFile ~/.ssh/id_ed25519
   ```

   Omit `UseKeychain` if you have no passphrase.

3. **Add key to ssh-agent**:

   ```zsh
   ssh-add --apple-use-keychain ~/.ssh/id_ed25519
   ```

This stores the passphrase in macOS Keychain — you'll only be asked once.

#### Windows (Git Bash)

Add to `~/.profile` or `~/.bashrc`:

```bash
env=~/.ssh/agent.env
agent_load_env () { test -f "$env" && . "$env" >| /dev/null ; }
agent_start () {
    (umask 077; ssh-agent >| "$env")
    . "$env" >| /dev/null ; }
agent_load_env
agent_run_state=$(ssh-add -l >| /dev/null 2>&1; echo $?)
if [ ! "$SSH_AUTH_SOCK" ] || [ $agent_run_state = 2 ]; then
    agent_start
    ssh-add
elif [ "$SSH_AUTH_SOCK" ] && [ $agent_run_state = 1 ]; then
    ssh-add
fi
unset env
```

Prompts once when Git Bash opens, then remembers for the session.

### References

- [Working with SSH key passphrases](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/working-with-ssh-key-passphrases)
- [Generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

## yt-dlp downloading audio-only webm

### Problem

yt-dlp downloads an audio-only `.webm` instead of video with audio.

### Fix

Explicitly specify video and audio streams and merge them:

```zsh
yt-dlp -f "bestvideo+bestaudio" --merge-output-format mp4 URL
```

Or prefer single-file formats to avoid merging:

```zsh
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" URL
```

Merging requires ffmpeg: `brew install ffmpeg`
