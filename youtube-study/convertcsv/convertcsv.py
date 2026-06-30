# convertcsv.py version 2.3.0
# For converting YouTube live chat text files manually copied from videos to CSV format.
# See CHANGELOG.md for version history.

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

# Pre-built translation table: maps zero-width chars + narrow no-break space to removal/space
_ZW_TABLE = str.maketrans({
    "\u200b": None,
    "\u200c": None,
    "\u200d": None,
    "\ufeff": None,
    "\u202f": " ",
})

_TIMESTAMP_RE = re.compile(r"^\d{1,2}:\d{2}\s*[AP][Mm]$", re.IGNORECASE)
_DOLLAR_RE = re.compile(r"^(?:[A-Z]{0,3}\$)?\d+(?:[.,]\d{2})?$")
_MEMBER_STATUS_RE = re.compile(r"^member\s+for\b", re.IGNORECASE)
_MEMBER_TIER_RE = re.compile(r".*\bmembers?\b$", re.IGNORECASE)


@dataclass
class MessageRow:
    timestamp: str = ""
    user: str = ""
    membership: str = ""
    member_status: str = ""
    member_tier: str = ""
    dollar_amount: str = ""
    message_lines: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.user and not self.message_lines

    def to_csv_row(self) -> list[str]:
        return [
            self.timestamp,
            self.user,
            self.membership,
            self.member_status,
            self.member_tier,
            self.dollar_amount,
            " ".join(self.message_lines),
        ]


def _normalize(line: str) -> str:
    return line.translate(_ZW_TABLE).strip()


def _is_timestamp(line: str) -> bool:
    return bool(_TIMESTAMP_RE.match(line))


def _is_membership_line(line: str) -> bool:
    lowered = line.lower()
    return lowered.startswith("new member") or lowered.startswith("member (")


def _is_member_status(line: str) -> bool:
    return bool(_MEMBER_STATUS_RE.match(line))


def _is_member_tier(line: str) -> bool:
    return not _is_membership_line(line) and bool(_MEMBER_TIER_RE.match(line))


def _is_dollar_amount(line: str) -> bool:
    return bool(_DOLLAR_RE.match(line.replace(",", "")))


def parse(raw_lines: list[str]) -> list[list[str]]:
    lines = [_normalize(l) for l in raw_lines]
    rows: list[MessageRow] = []
    current: MessageRow | None = None

    def finalize() -> None:
        nonlocal current
        if current and not current.is_empty():
            rows.append(current)
        current = None

    def peek_next_nonempty(idx: int) -> str:
        for j in range(idx + 1, len(lines)):
            if lines[j]:
                return lines[j]
        return ""

    for i, line in enumerate(lines):
        if not line:
            continue

        if _is_timestamp(line):
            finalize()
            current = MessageRow(timestamp=line)
            continue

        if line.startswith("@"):
            nxt = peek_next_nonempty(i)
            if current is None or (nxt and _is_membership_line(nxt) and current.user):
                finalize()
                current = MessageRow()
            if not current.user:
                current.user = line
            else:
                current.message_lines.append(line)
            continue

        if current is None:
            continue

        if not current.user:
            current.user = line
        elif not current.membership and _is_membership_line(line):
            current.membership = line
        elif not current.member_status and _is_member_status(line):
            current.member_status = line
        elif not current.member_tier and _is_member_tier(line):
            current.member_tier = line
        elif not current.dollar_amount and _is_dollar_amount(line):
            current.dollar_amount = line
        else:
            current.message_lines.append(line)

    finalize()
    return [row.to_csv_row() for row in rows]


_CSV_HEADER = ["timestamp", "user", "membership", "member_status", "member_tier", "dollar_amount", "message"]


def main() -> None:
    input_path_str = input("Enter input file name (e.g. input.txt): ").strip()
    if not input_path_str:
        raise ValueError("Input file name cannot be empty")

    input_path = Path(input_path_str)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = input_path.with_name(
        f"{input_path.stem}_output.csv" if input_path.suffix else f"{input_path.name}_output"
    )

    raw_lines = input_path.read_text(encoding="utf-8").splitlines()
    rows = parse(raw_lines)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_CSV_HEADER)
        writer.writerows(rows)

    print(f"Parsed {len(rows)} message rows from {input_path.name} to {output_path.name}")


if __name__ == "__main__":
    main()
