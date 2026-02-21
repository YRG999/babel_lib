# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-02-21

### Changed

- Replaced `ChatParser` class with module-level `parse()` function and standalone `MessageRow` dataclass.
- Replaced per-character `.replace()` loop with a single `str.translate()` call for zero-width and narrow no-break space cleanup.
- Switched from manual `while` index loops to `enumerate()` and `range()`.
- Replaced `open()` + `readlines()` with `read_text().splitlines()`.

### Removed

- `ChatParser` class (no meaningful reusable state between calls).
- `add_message_line()` wrapper (replaced with direct `.append()`).
- Redundant re-normalization inside timestamp check.

## [2.2.0] - 2025-12-05

### Added

- Parsing for member status, member tier, and dollar amount columns.

### Fixed

- Membership line detection no longer false-matches on "member for..." and "member tier..." lines (`startswith("member")` narrowed to `startswith("member (")`).

## [2.1.0] - 2025-12-05

### Changed

- Refactored into a `ChatParser` class with `MessageRow` dataclass.
- Wrapped script body in a `main()` function with `__main__` guard.

## [2.0.0] - 2025-12-05

### Added

- Structured block parsing for timestamps, user, membership, and message columns.
- Support for `@user` blocks without timestamps.
- Zero-width character and narrow no-break space cleanup.
- Interactive input/output file naming.

## [1.0.0] - 2025-11-28

### Added

- Initial one-column CSV conversion from plain text lists.
