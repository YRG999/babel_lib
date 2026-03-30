#!/usr/bin/env python3
"""
filter_chat.py — Filter repetitive and emote-only messages from Kick chat CSV.

Filters applied (in order):
  1. Emote-only: messages whose text is entirely [emote:ID:name] tags are removed.
  2. Internal repetition: messages where the same phrase is copy-pasted many
     times within a single message are removed.
  3. Per-user dedup: if a user posts the same message again within a rolling
     time window, the repeat is dropped.
  4. Reaction flood: short messages (reactions/memes) that have already
     appeared many times within a time window are dropped.
"""

import csv
import re
import sys
import argparse
from collections import defaultdict, deque
from pathlib import Path

EMOTE_RE = re.compile(r'\[emote:\d+:[^\]]+\]')


def strip_emotes(text):
    return EMOTE_RE.sub('', text).strip()


def normalize(text):
    """Lowercase, collapse whitespace, collapse 3+ repeated chars to 2."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    return text


def has_internal_repetition(text, ngram_words=5, min_repeats=3):
    """Return True if a word-sequence of ngram_words appears >= min_repeats times."""
    words = text.split()
    if len(words) < ngram_words * min_repeats:
        return False
    seen = defaultdict(int)
    for i in range(len(words) - ngram_words + 1):
        ng = ' '.join(words[i:i + ngram_words])
        seen[ng] += 1
        if seen[ng] >= min_repeats:
            return True
    return False


def parse_vod_offset(s):
    parts = s.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def main():
    parser = argparse.ArgumentParser(
        description='Filter repetitive and emote-only messages from Kick chat CSV',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('-o', '--output', help='Output CSV (default: <input>_filtered.csv)')
    parser.add_argument(
        '--user-dedup-window', type=int, default=120, metavar='SECS',
        help='Suppress same user posting the same message within this window',
    )
    parser.add_argument(
        '--reaction-window', type=int, default=30, metavar='SECS',
        help='Time window for reaction flood detection',
    )
    parser.add_argument(
        '--reaction-max', type=int, default=5, metavar='N',
        help='Max times a short reaction is kept per reaction window',
    )
    parser.add_argument(
        '--reaction-len', type=int, default=15, metavar='CHARS',
        help='Messages with text <= this length are treated as reactions',
    )
    parser.add_argument(
        '--no-emote-filter', action='store_true',
        help='Keep emote-only messages',
    )
    parser.add_argument(
        '--no-repeat-filter', action='store_true',
        help='Keep internally repetitive messages',
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Error: {input_path} not found', file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + '_filtered')

    # Per-user dedup: (user_id, normalized_text) -> last accepted vod offset seconds
    user_last_seen: dict[tuple, int] = {}
    # Reaction flood: normalized_text -> deque of vod offset seconds for recent occurrences
    reaction_times: dict[str, deque] = defaultdict(deque)

    kept = 0
    dropped_emote = 0
    dropped_internal_rep = 0
    dropped_user_dedup = 0
    dropped_reaction = 0
    total = 0

    with open(input_path, newline='', encoding='utf-8') as inf, \
         open(output_path, 'w', newline='', encoding='utf-8') as outf:

        reader = csv.DictReader(inf)
        if reader.fieldnames is None:
            print('Error: empty or invalid CSV', file=sys.stderr)
            sys.exit(1)

        writer = csv.DictWriter(outf, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            message = row['message']
            user_id = row['user_id']
            offset_s = parse_vod_offset(row['vod_offset'])

            # 1. Strip emotes and check if anything remains
            text = strip_emotes(message)
            if not args.no_emote_filter and not text:
                dropped_emote += 1
                continue

            # 2. Internal repetition (e.g. same phrase copy-pasted 3+ times)
            if not args.no_repeat_filter and text and has_internal_repetition(text):
                dropped_internal_rep += 1
                continue

            # 3. Per-user dedup: same user, same normalized message within window
            norm = normalize(text) if text else normalize(message)
            user_key = (user_id, norm)
            last_offset = user_last_seen.get(user_key)
            if last_offset is not None and (offset_s - last_offset) < args.user_dedup_window:
                dropped_user_dedup += 1
                continue
            user_last_seen[user_key] = offset_s

            # 4. Reaction flood: short messages seen too many times recently
            if len(text) <= args.reaction_len:
                norm_react = normalize(text) if text else normalize(message)
                q = reaction_times[norm_react]
                # Evict entries outside the window
                while q and (offset_s - q[0]) > args.reaction_window:
                    q.popleft()
                if len(q) >= args.reaction_max:
                    dropped_reaction += 1
                    continue
                q.append(offset_s)

            writer.writerow(row)
            kept += 1

    print(f'Input:  {total:,} messages')
    print(f'Output: {kept:,} messages kept ({kept / total * 100:.1f}%)')
    print(f'  Emote-only dropped:        {dropped_emote:,}')
    print(f'  Internal repetition dropped: {dropped_internal_rep:,}')
    print(f'  Per-user dedup dropped:    {dropped_user_dedup:,}')
    print(f'  Reaction flood dropped:    {dropped_reaction:,}')
    print(f'Written to: {output_path}')


if __name__ == '__main__':
    main()
