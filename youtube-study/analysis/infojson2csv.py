# infojson2csv.py version 1.1.0
# Parses yt-dlp .info.json files into a single CSV.
# Usage: python infojson2csv.py [DIRECTORY] [-o OUTPUT.csv] [--no-markdown]

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_SCALAR_FIELDS = [
    "id",
    "title",
    "channel",
    "channel_id",
    "channel_url",
    "uploader",
    "uploader_id",
    "uploader_url",
    "upload_date",
    "duration",
    "duration_string",
    "view_count",
    "like_count",
    "comment_count",
    "channel_follower_count",
    "webpage_url",
    "thumbnail",
    "age_limit",
    "availability",
    "live_status",
    "media_type",
    "width",
    "height",
    "fps",
    "resolution",
    "ext",
    "filesize_approx",
    "description",
]

_LIST_FIELDS = ["categories", "tags"]


def _default_stem() -> str:
    now = datetime.now(ZoneInfo("America/New_York"))
    return f"infojson_output_{now.strftime('%Y%m%d_%H%M%S')}"


def _extract(data: dict) -> dict:
    row = {}
    for field in _SCALAR_FIELDS:
        row[field] = data.get(field, "")
    for field in _LIST_FIELDS:
        val = data.get(field, [])
        row[field] = "; ".join(str(v) for v in val) if val else ""
    return row


def _find_info_jsons(root: Path) -> list[Path]:
    return sorted(root.rglob("*.info.json"))


def _write_markdown(output_path: Path, rows: list[dict]) -> Path:
    md_path = output_path.with_suffix(".md")
    with md_path.open("w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            if i > 0:
                f.write("\n---\n\n")
            title = str(row.get("title", "")).strip() or "(no title)"
            url = str(row.get("webpage_url", "")).strip()
            description = str(row.get("description", "")).strip()
            uploader_id = str(row.get("uploader_id", "")).strip()
            f.write(f"# {title}\n\n")
            if uploader_id:
                f.write(f"{uploader_id}\n\n")
            if url:
                f.write(f"**URL:** {url}\n\n")
            if description:
                f.write(f"{description}\n\n")
    return md_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert yt-dlp .info.json files to a CSV."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory to search for .info.json files (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV file path (default: <DIRECTORY>/infojson_output_<datetime_EST>.csv)",
    )
    parser.add_argument(
        "--markdown",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write a Markdown file with title, URL, and description (default: on)",
    )
    args = parser.parse_args()

    root = Path(args.directory).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    output_path = Path(args.output) if args.output else root / f"{_default_stem()}.csv"
    files = _find_info_jsons(root)

    if not files:
        print(f"No .info.json files found under {root}")
        return

    header = ["file_path"] + _SCALAR_FIELDS + _LIST_FIELDS
    rows: list[dict] = []

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for path in files:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                print(f"  Skipping {path.name}: {e}")
                continue

            row = _extract(data)
            row["file_path"] = str(path.relative_to(root))
            writer.writerow(row)
            rows.append(row)
            print(f"  {path.name}")

    print(f"\nWrote {len(rows)} rows to {output_path}")

    if args.markdown:
        md_path = _write_markdown(output_path, rows)
        print(f"Wrote markdown to {md_path}")


if __name__ == "__main__":
    main()
