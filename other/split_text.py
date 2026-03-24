#!/usr/bin/env python3
"""Split a text file into multiple files of at most MAX_CHARS characters each."""

import argparse
import os


def split_file(input_path: str, max_chars: int = 16000, output_dir: str = None) -> list[str]:
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if len(text) <= max_chars:
        print(f"File is {len(text)} chars — no splitting needed.")
        return [input_path]

    base = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1] or ".txt"
    out_dir = output_dir or os.path.dirname(os.path.abspath(input_path))

    chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
    pad = len(str(len(chunks)))
    output_files = []

    for i, chunk in enumerate(chunks, start=1):
        out_path = os.path.join(out_dir, f"{base}_part{str(i).zfill(pad)}{ext}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(chunk)
        output_files.append(out_path)
        print(f"  Wrote {out_path} ({len(chunk)} chars)")

    print(f"\nSplit into {len(chunks)} files.")
    return output_files


def main():
    parser = argparse.ArgumentParser(description="Split a text file into chunks.")
    parser.add_argument("input", help="Path to the input text file")
    parser.add_argument(
        "-n", "--max-chars", type=int, default=16000,
        help="Max characters per output file (default: 16000)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory for output files (default: same as input file)"
    )
    args = parser.parse_args()
    split_file(args.input, args.max_chars, args.output_dir)


if __name__ == "__main__":
    main()
