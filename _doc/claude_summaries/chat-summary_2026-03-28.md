# Chat Summary — 2026-03-28

## Overview

This session covered: Claude Code skills overview, consolidating `add_vod_offset.py` into `youtube-downloader-app`, and reorganizing the two programming notes files into `_doc/`.

---

## 1. Claude Code skills

Discussed the available slash-command skills in Claude Code:

| Skill | Purpose |
| --- | --- |
| `/simplify` | Reviews recently changed code for quality, redundancy, and efficiency, then fixes issues |
| `/update-config` | Configures `settings.json` (hooks, permissions, env vars) using plain English |
| `/loop` | Runs a prompt on a recurring interval (e.g. `/loop 5m check output folders`) |
| `/schedule` | Creates a scheduled remote agent on a cron schedule |
| `/keybindings-help` | Customizes keyboard shortcuts in `~/.claude/keybindings.json` |
| `/claude-api` | Scaffolds apps using the Anthropic SDK or Claude Agent SDK |

Notes added to `_doc/programming_notes.md` under a new `## Claude Code skills` section.

---

## 2. Consolidate `add_vod_offset.py` into `youtube-downloader-app`

`_notes/scripts/add_vod_offset.py` moved into the main project alongside similar standalone utilities (`timestamp_converter.py`, `firefox_cookie_export.py`).

| File | Change |
| --- | --- |
| `src/add_vod_offset.py` | Moved from `_notes/scripts/` |
| `README.md` | Added to project structure tree; added `### Backfill: vod_offset for existing CSVs` section under Kick.com |
| `CHANGELOG.md` | Added as second bullet under `[2.1.1] - 2026-03-26 ### Added` |
| `CLAUDE.md` | Added to Key Files table; removed stale `utils.py`/`extract_functions.py` references |
| `_notes/scripts/add_vod_offset.py` | Deleted (moved) |
| `_notes/scripts/README.md` | Deleted (consolidated into main README) |
| `_notes/scripts/CHANGELOG.md` | Deleted (consolidated into main CHANGELOG) |

---

## 3. Consolidate programming notes into `_doc/`

`_doc/Programming_notes.md` (renamed by user to `programming_reference.md`) and `_notes/markdown/programming_notes.md` were identified as serving different purposes and kept as separate files.

**Distinction:**

| File | Purpose |
| --- | --- |
| `_doc/programming_reference.md` | Thematic reference — API links, how-to notes, reference tables organized by topic |
| `_doc/programming_notes.md` | Troubleshooting log — dated problem/cause/fix entries |

Both files were given a tagline at the top describing what to add and linking to the other. `programming_notes.md` was moved from `_notes/markdown/` to `_doc/` to co-locate both files.

A `## Notes` section pointing to both files was added to `youtube-downloader-app/CLAUDE.md`, `ytdownload/CLAUDE.md`, and `ytdownload/claude.md`.

| File | Change |
| --- | --- |
| `_doc/programming_reference.md` | Updated title; added description tagline |
| `_doc/programming_notes.md` | Moved from `_notes/markdown/`; added description tagline |
| `_notes/markdown/programming_notes.md` | Deleted (moved) |
| `youtube-downloader-app/CLAUDE.md` | Added `## Notes` section |
| `ytdownload/CLAUDE.md` | Added `## Notes` section (see note below) |

**Note: `CLAUDE.md` must be uppercase.** Claude Code auto-loads context files named `CLAUDE.md` at the start of each session. Lowercase `claude.md` is not recognized and will be silently ignored. On macOS (case-insensitive filesystem) `CLAUDE.md` and `claude.md` refer to the same file, so edits to either name go to the same place — there is only ever one file.

---

## 4. Debugging `kick_live_downloader.py` — `--use-profile` errors

A series of 6 sequential errors were debugged while getting `--use-profile` working. All fixes applied to `src/kick_live_downloader.py`. Progress tracked in `_notes/txt/error.txt`.

| Error | Root Cause | Fix |
| --- | --- | --- |
| 1 | `ModuleNotFoundError: playwright` | Install: `pip install playwright && python -m playwright install` |
| 2 | `launch_persistent_context` timeout — headless renderer fails with real Firefox profile (`RenderCompositorSWGL`) | Force headful mode when `--use-profile` is set |
| 3 | Same GPU Helper / XPC timeout even with headful + copied temp profile | Dropped `launch_persistent_context` entirely; switched to extracting cookies via `browser_cookie3` and injecting into a regular context with `add_cookies` |
| 4 | `add_cookies` rejected all cookies — session cookies with `expires=0` were passed without an `expires` field, Playwright defaulted to `0` internally which it rejects | Always set `expires` explicitly: positive int for persistent cookies, `-1` for session cookies |
| 5 | Same error persisted — bulk `add_cookies` call gave no info on which cookie failed | Add cookies one at a time with per-cookie `try/except`; print name + expires on failure; tightened validation (skip missing name/domain, coerce to `int`) |
| 6 | All 14 cookies skipped — `expires` values like `1765827144841` are milliseconds, Playwright expects seconds | Detect ms timestamps (`> 32503680000`) and divide by 1000 before passing to Playwright |

Error 6 fix was applied but not yet tested at end of session. See `_notes/txt/error.txt` for full error output and next-steps context.
