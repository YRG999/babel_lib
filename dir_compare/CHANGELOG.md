# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-02

### Added

- `--compare` mode: bidirectional comparison that lists files missing from either directory.
- `compare_dirs()` function using a `log()` helper (via `tee`) to print results to console and write them to a timestamped `dir_compare_YYYYMMDD_HHMMSS.txt` file simultaneously.
- `list_files()` helper that encapsulates null-delimited, sorted file listing; shared by both compare and copy logic.

## [1.0.0] - 2026-03-24

### Added

- Initial script: one-directional comparison that copies files from a source directory to a destination directory when they don't exist at the same relative path in the destination.
- `--dry-run` mode to preview what would be copied without making changes.
- Handles filenames with spaces and special characters via null-delimited `find` output.
- Uses `cp -a` to preserve timestamps and permissions.
- Creates intermediate parent directories as needed.
