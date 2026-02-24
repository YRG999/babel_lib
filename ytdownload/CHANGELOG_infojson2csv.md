# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-24

### Added

- `--markdown` / `--no-markdown` flag (default: on) that writes a `.md` file alongside the CSV, containing title, uploader ID, URL, and description for each video.
- EST datetime timestamp in the default output filename (`infojson_output_YYYYMMDD_HHMMSS.csv`).

### Changed

- Default output path is now the search directory itself rather than the current working directory.

## [1.0.0] - 2026-02-24

### Added

- Initial release.
- Recursively finds all `.info.json` files under a given directory.
- Extracts 29 metadata fields per video into a single CSV (scalar fields and list fields joined with "; ").
- `file_path` column with path relative to the search root.
- `-o` / `--output` argument for custom output path.
- Skips unparseable files with a warning rather than crashing.
