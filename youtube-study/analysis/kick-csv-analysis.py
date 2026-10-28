#!/usr/bin/env python3
"""
kick-csv-analysis.py — Sentiment analysis of a Kick VOD chat CSV.

Reads the chat CSV produced by youtube-downloader-app/src/kick_vod_downloader.py
and scores each message with VADER (rule-based, tuned for social media/chat).
Only these columns are used: vod_offset, timestamp, username, message, type.

--filter picks what is analysed:
  none      the raw CSV (default)
  filtered  the CSV after filter_chat.py (same folder) removes emote-only
            messages, repeats and reaction floods
  compare   both, printing raw vs. filtered overall and time-bucket tables

Outputs:
  - <input>_sentiment.csv and/or <input>_filtered_sentiment.csv: one row per
    message with VADER scores and a label.
  - A printed summary: overall breakdown, sentiment over time (by vod_offset),
    by message type, most positive/negative users, and extreme messages
    (or, with --filter compare, the raw vs. filtered comparison).
"""

import csv
import re
import sys
import argparse
import subprocess
from collections import defaultdict
from pathlib import Path

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print('Error: vaderSentiment is not installed. Run: pip install -r requirements.txt',
          file=sys.stderr)
    sys.exit(1)

REQUIRED_COLUMNS = ['vod_offset', 'timestamp', 'username', 'message', 'type']
OUTPUT_COLUMNS = ['vod_offset', 'timestamp', 'username', 'type', 'message',
                  'compound', 'pos', 'neu', 'neg', 'label']
FILTER_SCRIPT = Path(__file__).resolve().with_name('filter_chat.py')

# VADER authors' standard cutoff. Most chat scores exactly 0 (unknown words such
# as emote names), so raising this mainly drops weak reactions like "gg"/"lol".
LABEL_THRESHOLD = 0.05

# --filter compare: when divergence_note() flags a time bucket. Tuned on an ~8k
# message chat: at 5-min buckets, emote-heavy flags ~10% of buckets and mean
# shifts ~3%; mood flips are rare (filtering removes mostly 0-score messages).
NOTE_MIN_MSGS = 10            # raw messages needed before a bucket can be flagged
NOTE_EMOTE_HEAVY_KEPT = 0.5   # flag if filtering keeps under this share of messages
NOTE_MEAN_SHIFT = 0.1         # flag if mean compound moves at least this much
NOTE_LEGEND = [
    ('mood flips', 'raw leans positive but filtered leans negative, or the reverse'),
    ('emote-heavy', f'filtering removed over {1 - NOTE_EMOTE_HEAVY_KEPT:.0%} of messages '
                    '(often a hype/reaction moment)'),
    ('mean shifts', f'mean compound changed by {NOTE_MEAN_SHIFT} or more '
                    '(a strongly emotional moment where many neutral messages were removed)'),
]

# Bot check (check_bots). Flags users only; exclusion is up to --exclude-users.
# Chat-bot services common on Kick/Twitch, compared case-insensitively.
KNOWN_BOTS = {'botrix', 'kickbot', 'kicklet', 'nightbot', 'streamelements', 'streamlabs',
              'fossabot', 'moobot', 'sery_bot', 'wizebot'}
BOT_NAME_RE = re.compile(r'^bot|bots?\d*$', re.IGNORECASE)  # "BotRix", "examplebot42"
URL_RE = re.compile(r'https?://|www\.', re.IGNORECASE)
BOT_LINK_SHARE = 0.5     # flag users whose messages are mostly links...
BOT_LINK_MIN_MSGS = 5    # ...once they have at least this many messages

# Same pattern as filter_chat.py, with a capture group for the emote name
EMOTE_RE = re.compile(r'\[emote:\d+:([^\]]+)\]')


def emotes_to_names(text):
    """Replace [emote:ID:name] tags with the bare name so VADER sees a word."""
    return EMOTE_RE.sub(r' \1 ', text).strip()


def parse_vod_offset(s):
    parts = s.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def format_hms(secs):
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02}:{s:02}'


def classify(compound):
    """Map a VADER compound score (-1.0 to 1.0) to 'positive', 'negative' or 'neutral'."""
    if compound >= LABEL_THRESHOLD:
        return 'positive'
    if compound <= -LABEL_THRESHOLD:
        return 'negative'
    return 'neutral'


def mean(values):
    return sum(values) / len(values) if values else 0.0


def pct(part, whole):
    return part / whole * 100 if whole else 0.0


def group_stats(group):
    """Return (messages, mean compound, % positive, % negative) for a list of rows."""
    n = len(group)
    return (n, mean([r['compound'] for r in group]),
            pct(sum(r['label'] == 'positive' for r in group), n),
            pct(sum(r['label'] == 'negative' for r in group), n))


def bucket_by_offset(scored, bucket_secs):
    """Group scored rows by vod_offset bucket index. Rows without an offset are skipped."""
    buckets = defaultdict(list)
    for r in scored:
        if r['_offset_s'] is not None:
            buckets[r['_offset_s'] // bucket_secs].append(r)
    return buckets


def bucket_label(b, bucket_secs):
    return f'{format_hms(b * bucket_secs)}–{format_hms((b + 1) * bucket_secs)}'


def load_rows(input_path):
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print(f'Error: {input_path} is empty or not a valid CSV', file=sys.stderr)
            sys.exit(1)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            print(f'Error: CSV is missing column(s): {", ".join(missing)}', file=sys.stderr)
            sys.exit(1)
        return [{c: row[c] or '' for c in REQUIRED_COLUMNS} for row in reader]


def score_rows(rows):
    """Add VADER scores and a label to each row. Blank messages are not scored."""
    analyzer = SentimentIntensityAnalyzer()
    for row in rows:
        text = emotes_to_names(row['message'])
        if text:
            scores = analyzer.polarity_scores(text)
            row.update({k: round(scores[k], 4) for k in ('compound', 'pos', 'neu', 'neg')})
            row['label'] = classify(scores['compound'])
            row['_scored'] = True
        else:
            row.update({'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0, 'label': 'neutral'})
            row['_scored'] = False
        try:
            row['_offset_s'] = parse_vod_offset(row['vod_offset'])
        except (ValueError, IndexError):
            row['_offset_s'] = None


def write_csv(rows, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def analyze_file(input_path, output_path, excluded):
    """Load, score and write one CSV, leaving out excluded users; return its rows."""
    rows = [r for r in load_rows(input_path) if r['username'].lower() not in excluded]
    if not rows:
        print(f'Error: {input_path} has no messages (after --exclude-users)', file=sys.stderr)
        sys.exit(1)
    score_rows(rows)
    write_csv(rows, output_path)
    return rows


def run_filter_chat(input_path):
    """Run filter_chat.py (default settings) on input_path; return the filtered CSV path."""
    filtered_path = input_path.with_stem(input_path.stem + '_filtered')
    result = subprocess.run(
        [sys.executable, str(FILTER_SCRIPT), '-o', str(filtered_path), '--', str(input_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f'Error: filter_chat.py failed:\n{result.stderr.strip()}', file=sys.stderr)
        sys.exit(1)
    print('## filter_chat.py\n')
    print(result.stdout.strip())
    print()
    return filtered_path


def check_bots(rows):
    """Return {username: (messages, [signals], likely)} for users that look like bots."""
    by_user = defaultdict(list)
    for r in rows:
        by_user[r['username']].append(r['message'])
    suspects = {}
    for user, msgs in by_user.items():
        signals = []
        likely = user.lower() in KNOWN_BOTS
        if likely:
            signals.append('known chat-bot account')
        elif BOT_NAME_RE.search(user):
            signals.append('name contains "bot"')
        link_share = sum(bool(URL_RE.search(m)) for m in msgs) / len(msgs)
        if len(msgs) >= BOT_LINK_MIN_MSGS and link_share >= BOT_LINK_SHARE:
            signals.append(f'{link_share:.0%} of messages are links')
        if signals:
            suspects[user] = (len(msgs), signals, likely)
    return suspects


def print_bot_check(rows, excluded):
    """Print suspected bots and excluded users. rows: the raw chat, before any exclusion."""
    suspects = check_bots(rows)
    counts = defaultdict(int)
    names = {}
    for r in rows:
        counts[r['username']] += 1
        names[r['username'].lower()] = r['username']
    listed = set(suspects) | {names[e] for e in excluded if e in names}

    print('\n## Bot check\n')
    if listed:
        print('| User | Messages | Signals | Status |')
        print('| --- | ---: | --- | --- |')
        for user in sorted(listed, key=lambda u: -counts[u]):
            signals, likely = suspects[user][1:] if user in suspects else ([], False)
            if user.lower() in excluded:
                status = 'excluded'
            elif likely:
                status = f'likely bot, should be excluded: `--exclude-users {user}`'
            else:
                status = f'possible bot, check its messages; to exclude: `--exclude-users {user}`'
            print(f'| {user} | {counts[user]:,} | {"; ".join(signals) or "none (excluded by you)"} '
                  f'| {status} |')
        print('\nMessage counts are from the raw chat. Signals: known chat-bot service names, '
              f'{BOT_LINK_SHARE:.0%}+ of messages containing links, or "bot" at the start/end '
              'of the name. Only users named in --exclude-users are left out of the analysis.')
    else:
        print('No likely bots found.')
    for name in sorted(excluded - names.keys()):
        print(f'\nWarning: --exclude-users {name}: no such user in this chat.')


def print_group_table(title, key_header, groups):
    """groups: list of (key, [rows]) in display order."""
    print(f'\n## {title}\n')
    print(f'| {key_header} | Messages | Mean compound | % pos | % neg |')
    print('| --- | ---: | ---: | ---: | ---: |')
    for key, group in groups:
        n, avg, ppos, pneg = group_stats(group)
        print(f'| {key} | {n:,} | {avg:+.3f} | {ppos:.1f} | {pneg:.1f} |')


def print_summary(rows, bucket_mins, top_n, min_msgs):
    scored = [r for r in rows if r['_scored']]
    n = len(scored)
    counts = defaultdict(int)
    for r in scored:
        counts[r['label']] += 1

    print('# Kick chat sentiment summary\n')
    print(f'Messages: {len(rows):,} ({len(rows) - n:,} blank, not scored)')
    print(f'Mean compound: {mean([r["compound"] for r in scored]):+.3f}')
    for label in ('positive', 'neutral', 'negative'):
        print(f'  {label:<9} {counts[label]:>8,}  ({pct(counts[label], n):.1f}%)')

    # Sentiment over time
    bucket_secs = bucket_mins * 60
    buckets = bucket_by_offset(scored, bucket_secs)
    print_group_table(
        f'Sentiment over time ({bucket_mins}-min buckets)', 'VOD offset',
        [(bucket_label(b, bucket_secs), buckets[b]) for b in sorted(buckets)],
    )

    # By message type
    by_type = defaultdict(list)
    for r in scored:
        by_type[r['type'] or '(none)'].append(r)
    print_group_table('By message type', 'Type',
                      sorted(by_type.items(), key=lambda kv: -len(kv[1])))

    # Users
    by_user = defaultdict(list)
    for r in scored:
        by_user[r['username']].append(r)
    print_group_table(f'Most active users ({len(by_user):,} users in total)', 'User',
                      sorted(by_user.items(), key=lambda kv: -len(kv[1]))[:top_n])
    eligible = [(u, msgs) for u, msgs in by_user.items() if len(msgs) >= min_msgs]
    eligible.sort(key=lambda kv: mean([r['compound'] for r in kv[1]]))
    print_group_table(f'Most positive users (≥ {min_msgs} messages)', 'User',
                      list(reversed(eligible[-top_n:])))
    print_group_table(f'Most negative users (≥ {min_msgs} messages)', 'User',
                      eligible[:top_n])

    # Extreme messages
    by_score = sorted(scored, key=lambda r: r['compound'])
    positives = [r for r in reversed(by_score) if r['compound'] > 0][:top_n]
    negatives = [r for r in by_score if r['compound'] < 0][:top_n]
    for title, picks in (('Most positive messages', positives),
                         ('Most negative messages', negatives)):
        print(f'\n## {title}\n')
        print('| VOD offset | User | Compound | Message |')
        print('| --- | --- | ---: | --- |')
        for r in picks:
            msg = r['message'].replace('|', '\\|').replace('\n', ' ')
            if len(msg) > 100:
                msg = msg[:97] + '...'
            print(f'| {r["vod_offset"]} | {r["username"]} | {r["compound"]:+.3f} | {msg} |')


def divergence_note(raw_stats, filt_stats):
    """Short note for a time bucket where filtering changes the picture, else ''.

    Each argument is a group_stats() tuple: (messages, mean, % pos, % neg).
    Notes (see NOTE_LEGEND): 'mood flips', 'emote-heavy', 'mean shifts'.
    """
    raw_n, raw_mean, raw_pos, raw_neg = raw_stats
    filt_n, filt_mean, filt_pos, filt_neg = filt_stats
    if raw_n < NOTE_MIN_MSGS:
        return ''  # too few messages for percentages to mean anything
    if filt_n == 0:
        return 'emote-heavy'  # every message in the bucket was filtered out

    notes = []
    # Opposite lean: positive outnumbers negative on one side, the reverse on the other
    if (raw_pos - raw_neg) * (filt_pos - filt_neg) < 0:
        notes.append('mood flips')
    if filt_n < raw_n * NOTE_EMOTE_HEAVY_KEPT:
        notes.append('emote-heavy')
    if abs(raw_mean - filt_mean) >= NOTE_MEAN_SHIFT:
        notes.append('mean shifts')
    return ', '.join(notes)


def print_comparison(raw_rows, filt_rows, bucket_mins):
    raw = [r for r in raw_rows if r['_scored']]
    filt = [r for r in filt_rows if r['_scored']]

    print('# Kick chat sentiment: raw vs. filtered\n')
    print('| | Raw | Filtered |')
    print('| --- | ---: | ---: |')
    (rn, ravg, _, _), (fn, favg, _, _) = group_stats(raw), group_stats(filt)
    print(f'| Messages scored | {rn:,} | {fn:,} |')
    print(f'| Mean compound | {ravg:+.3f} | {favg:+.3f} |')
    for label in ('positive', 'neutral', 'negative'):
        rp = pct(sum(r['label'] == label for r in raw), rn)
        fp = pct(sum(r['label'] == label for r in filt), fn)
        print(f'| % {label} | {rp:.1f} | {fp:.1f} |')

    bucket_secs = bucket_mins * 60
    raw_buckets = bucket_by_offset(raw, bucket_secs)
    filt_buckets = bucket_by_offset(filt, bucket_secs)
    print(f'\n## Sentiment over time ({bucket_mins}-min buckets)\n')
    print('| VOD offset | Raw msgs | Filt msgs | Raw mean | Filt mean '
          '| Raw % pos/neg | Filt % pos/neg | Note |')
    print('| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |')
    for b in sorted(set(raw_buckets) | set(filt_buckets)):
        rs, fs = group_stats(raw_buckets[b]), group_stats(filt_buckets[b])
        print(f'| {bucket_label(b, bucket_secs)} | {rs[0]:,} | {fs[0]:,} '
              f'| {rs[1]:+.3f} | {fs[1]:+.3f} '
              f'| {rs[2]:.1f} / {rs[3]:.1f} | {fs[2]:.1f} / {fs[3]:.1f} '
              f'| {divergence_note(rs, fs)} |')
    print(f'\nNote column (buckets with ≥ {NOTE_MIN_MSGS} raw messages only):')
    for note, meaning in NOTE_LEGEND:
        print(f'- **{note}**: {meaning}')


def main():
    parser = argparse.ArgumentParser(
        description='Sentiment analysis (VADER) of a Kick VOD chat CSV',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input', help='Input Kick chat CSV (<title>_chat.csv)')
    parser.add_argument('-o', '--output',
                        help='Output CSV (default: <input>_sentiment.csv, or '
                             '<input>_filtered_sentiment.csv with --filter filtered; '
                             'not allowed with --filter compare)')
    parser.add_argument('--filter', choices=['none', 'filtered', 'compare'], default='none',
                        help='Analyse the raw CSV, the CSV after filter_chat.py, '
                             'or both side by side')
    parser.add_argument('--exclude-users', action='append', default=[], metavar='NAMES',
                        help='Comma-separated usernames to leave out of the analysis, '
                             'e.g. bots (case-insensitive; can be repeated)')
    parser.add_argument('--bucket', type=int, default=5, metavar='MINS',
                        help='Time bucket size for sentiment over time')
    parser.add_argument('--top', type=int, default=10, metavar='N',
                        help='How many users/messages to list in each top section')
    parser.add_argument('--min-msgs', type=int, default=5, metavar='N',
                        help='Minimum messages for a user to be ranked')
    args = parser.parse_args()

    if args.bucket < 1 or args.top < 1 or args.min_msgs < 1:
        parser.error('--bucket, --top and --min-msgs must be at least 1')
    if args.filter == 'compare' and args.output:
        parser.error('-o/--output cannot be used with --filter compare (it writes two CSVs)')

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Error: {input_path} not found', file=sys.stderr)
        sys.exit(1)

    excluded = {name.strip().lower() for arg in args.exclude_users
                for name in arg.split(',') if name.strip()}
    raw_chat = load_rows(input_path)  # bot check always looks at the full, unfiltered chat

    def sentiment_path(p):
        return p.with_stem(p.stem + '_sentiment')

    if args.filter == 'none':
        output_path = Path(args.output) if args.output else sentiment_path(input_path)
        rows = analyze_file(input_path, output_path, excluded)
        print_summary(rows, args.bucket, args.top, args.min_msgs)
        print_bot_check(raw_chat, excluded)
        print(f'\nWritten to: {output_path}')
        return

    filtered_path = run_filter_chat(input_path)

    if args.filter == 'filtered':
        output_path = Path(args.output) if args.output else sentiment_path(filtered_path)
        rows = analyze_file(filtered_path, output_path, excluded)
        print_summary(rows, args.bucket, args.top, args.min_msgs)
        print_bot_check(raw_chat, excluded)
        print(f'\nWritten to: {output_path}')
        return

    raw_out, filt_out = sentiment_path(input_path), sentiment_path(filtered_path)
    raw_rows = analyze_file(input_path, raw_out, excluded)
    filt_rows = analyze_file(filtered_path, filt_out, excluded)
    print_comparison(raw_rows, filt_rows, args.bucket)
    print_bot_check(raw_chat, excluded)
    print(f'\nWritten to: {raw_out}\n            {filt_out}')


if __name__ == '__main__':
    main()
