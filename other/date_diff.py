#!/usr/bin/env python3
"""Calculate the number of days between two dates."""

from datetime import date


def parse_date(prompt: str) -> date:
    from datetime import datetime
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%B %d, %Y", "%b %d, %Y", "%m-%d-%Y", "%m-%d-%y"]
    raw = input(prompt).strip()
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: '{raw}'. Try formats like 2023-04-18 or April 18, 2023")


def main():
    print("Days Between Dates Calculator")
    print("Accepted formats: 2023-04-18 | 04/18/2023 | April 18, 2023\n")

    start = parse_date("Start date: ")
    end = parse_date("End date:   ")

    delta = end - start
    days = delta.days

    if days > 0:
        print(f"\n{days} days from {start} to {end}")
    elif days < 0:
        print(f"\n{abs(days)} days from {end} to {start} (end is before start)")
    else:
        print("\nSame date — 0 days apart")


if __name__ == "__main__":
    main()
