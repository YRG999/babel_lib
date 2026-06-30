# Chat Summary — 2026-06-30

## 1. Word frequency analyzer (`youtube-study/word_frequency/word_freq.py`)

Created a new stand-alone CLI tool that reads a UTF-8 text file (e.g. a cleaned-up transcript) and lists words appearing more than N times (default 10), after filtering a comprehensive hardcoded English stopword list (articles, conjunctions, prepositions, pronouns, auxiliary verbs, filler words, and common contractions). Goal is to surface names, places, and meaningful topic words. Results are printed to stdout and saved as `<input_stem>_freq.txt` alongside the input file.

- `--min-count N` flag to override the threshold.
- Tokenization: lowercase, strip punctuation (preserving contractions and hyphens), skip tokens under 2 characters or purely numeric.

## 2. `youtube-study/` folder — new top-level analysis hub

Created `youtube-study/` as a canonical home for stand-alone tools that analyze files produced by `youtube-downloader-app` and `ytdownload`. None of these scripts are imported by the downloaders — all are run manually after a download.

### What moved where

**`youtube-study/convertcsv/`** — moved from `ytdownload/convertcsv/` (v2.3.0, the current version).

**`youtube-study/analysis/`** — five standalone scripts confirmed safe to move by checking that no other file imports them:

| Script | Moved from |
| --- | --- |
| `analyze.py` | `ytdownload/` |
| `infojson2csv.py` | `ytdownload/` |
| `filter_chat.py` | `youtube-downloader-app/src/` |
| `add_vod_offset.py` | `youtube-downloader-app/src/` |
| `timestamp_converter.py` | `youtube-downloader-app/src/` |

Four scripts were confirmed **not** moveable because `youtube-downloader-app/src/main.py` imports them directly as part of the download pipeline: `livechat_to_csv.py`, `vtt_to_text.py`, `remove_dupe_lines.py`, `extract_comments.py`.

Each `youtube-study/` subfolder has its own README (with per-script descriptions and source provenance) and CHANGELOG.

### CLAUDE.md and README.md updates

- `ytdownload/CLAUDE.md` — removed moved scripts, added pointer to `youtube-study/analysis/`.
- `youtube-downloader-app/CLAUDE.md` — removed moved scripts, added pointer to `youtube-study/analysis/`.
- Root `CLAUDE.md` — added `youtube-study/` submodule entry; clarified no root-level `CHANGELOG.md`; added rule that session summaries should not mention changes to gitignored directories.
- Root `README.md` — removed `ytdownload/analyze.py` reference, added `### youtube-study` section.

## 3. TODOs added to `_doc/programming_reference.md`

- **Option 3 shared library refactor** — plan for moving the four pipeline-integrated post-processing scripts into a `shared/` package at the repo root, using `pyproject.toml` + `pip install -e .` so both `youtube-downloader-app` and `youtube-study` can import from it without `sys.path` hacks.
- **Test all youtube-study scripts** — table listing each script, its expected input file type, and what to verify.
