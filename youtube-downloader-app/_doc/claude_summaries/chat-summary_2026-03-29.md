# Session Summary — 2026-03-29

## Added `filter_chat.py` — Kick chat noise filter

Created `src/filter_chat.py`, a standalone CLI that reduces a Kick VOD chat CSV to its substantive messages by applying four sequential filters.

### Motivation

Tested against an 18-hour Kick VOD chat export (~195,600 messages). The chat was heavily polluted with emote-only reactions, copy-paste spam, users repeatedly posting the same message, and reaction floods (many users posting identical short strings like "L" or "W").

### Filters and results

| Filter | Dropped |
|--------|---------|
| Emote-only messages | 63,398 |
| Internal repetition (copy-paste spam) | 16,611 |
| Per-user dedup (same message within 2 min) | 44,089 |
| Reaction flood (short message threshold) | 637 |
| **Total kept** | **70,877 / 195,612 (36%)** |

### How the filters work

1. **Emote-only** — strips `[emote:ID:name]` tokens; if nothing remains, the message is dropped.
2. **Internal repetition** — splits message text into words and checks if any 5-word n-gram appears 3+ times; if so, the message is dropped as copy-paste spam.
3. **Per-user dedup** — tracks `(user_id, normalized_text)` → last accepted VOD offset. If the same user posts the same message again within the window (default: 120 s), the repeat is dropped. Normalization collapses repeated characters (LLLLL → ll) and lowercases.
4. **Reaction flood** — messages at or under 15 characters are treated as reactions. A sliding deque tracks recent occurrences; once a reaction has appeared 5+ times in the last 30 seconds, further occurrences are dropped.

All thresholds are CLI flags (`--user-dedup-window`, `--reaction-window`, `--reaction-max`, `--reaction-len`). Individual filters can be disabled with `--no-emote-filter` / `--no-repeat-filter`.

Output is written to `<input>_filtered.csv`; the original is not modified.

### Docs updated

- `README.md`: added `filter_chat.py` to the project structure and a new "Filtering chat noise" section with a usage table.
- `CHANGELOG.md`: added entry under `[Unreleased]`.
- `CLAUDE.md`: added `filter_chat.py` to the Key Files table.
