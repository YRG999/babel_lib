#!/usr/bin/env python3
"""
Add vod_offset column to an existing Kick VOD chat CSV.

Usage:
    python add_vod_offset.py <chat.csv> [metadata.json]

If metadata.json is omitted, looks for it in the same folder as the CSV.
The vod_offset column (H:MM:SS) is inserted as the first column.
Output is written to <original_name>_with_offset.csv.
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_kick_datetime(s: str) -> datetime:
    for fmt in (
        "%Y-%m-%d %H:%M:%S UTC",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
    ):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Could not parse datetime: {s!r}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    if len(sys.argv) >= 3:
        meta_path = Path(sys.argv[2])
    else:
        meta_path = csv_path.parent / "metadata.json"

    if not meta_path.exists():
        print(f"Error: {meta_path} not found. Pass metadata.json as second argument.")
        sys.exit(1)

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    livestream = meta.get("livestream") or {}
    start_time_str = livestream.get("start_time") or meta.get("start_time", "")
    if not start_time_str:
        print("Error: start_time not found in metadata.json.")
        sys.exit(1)

    start_dt = parse_kick_datetime(start_time_str)
    print(f"VOD start time: {start_dt.isoformat()}")

    out_path = csv_path.with_name(csv_path.stem + "_with_offset.csv")

    with open(csv_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        if reader.fieldnames is None:
            print("Error: CSV appears to be empty.")
            sys.exit(1)

        # Prepend vod_offset; skip it if already present
        fieldnames = list(reader.fieldnames)
        if "vod_offset" in fieldnames:
            fieldnames.remove("vod_offset")
        fieldnames = ["vod_offset"] + fieldnames

        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        skipped = 0
        for i, row in enumerate(reader, 1):
            ts = row.get("timestamp", "")
            try:
                msg_dt = parse_kick_datetime(ts)
                offset_secs = int((msg_dt - start_dt).total_seconds())
                h, rem = divmod(max(offset_secs, 0), 3600)
                m, s = divmod(rem, 60)
                row["vod_offset"] = f"{h}:{m:02}:{s:02}"
            except ValueError:
                row["vod_offset"] = ""
                skipped += 1

            writer.writerow(row)

            if i % 50000 == 0:
                print(f"  {i:,} rows processed...")

    print(f"Done. {i:,} rows written to {out_path}")
    if skipped:
        print(f"  {skipped} rows had unparseable timestamps (vod_offset left blank).")


if __name__ == "__main__":
    main()
