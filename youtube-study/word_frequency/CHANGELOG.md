# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-30

### Added

- Initial release.
- Reads a UTF-8 text file and counts word frequencies after stripping punctuation and normalizing to lowercase.
- Filters a comprehensive hardcoded English stopword list covering articles, conjunctions, prepositions, pronouns, auxiliary verbs, filler words, and common contractions.
- Skips purely numeric tokens and tokens shorter than two characters.
- Outputs results sorted by frequency descending, printed to console and saved as `<input_stem>_freq.txt` alongside the input file.
- `--min-count N` flag to set the minimum occurrence threshold (default: 10).
