# csv_to_livechat.py
# Converts livechat.py CSV output to yt-dlp .live_chat.json format
# for use with mpv-youtube-chat (https://github.com/BanchouBoo/mpv-youtube-chat)
#
# NOTE: This script has not been tested. Use with caution.
#
# Usage:
#   python csv_to_livechat.py chat_log.csv                        # prompts for stream start time
#   python csv_to_livechat.py chat_log.csv video.info.json        # reads start time from info.json
#   python csv_to_livechat.py chat_log.csv --start "2024-01-15 20:00:00 EST"
#   python csv_to_livechat.py chat_log.csv --video stream.mp4     # compare video creation_time vs first chat message

import csv
import json
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
import pytz
from dateutil import parser as dateutil_parser


EASTERN = pytz.timezone('US/Eastern')


def load_start_time_from_infojson(info_path: Path) -> Optional[datetime]:
    with open(info_path, encoding='utf-8') as f:
        info = json.load(f)
    # release_timestamp is the live stream start; timestamp is publish time
    ts = info.get('release_timestamp') or info.get('timestamp')
    if ts:
        return datetime.fromtimestamp(ts, tz=pytz.UTC)
    return None


def parse_start_time(ts_str: str) -> datetime:
    """Parse a start time that may be a Unix timestamp (int/float) or a date string."""
    ts_str = ts_str.strip()
    try:
        unix_ts = float(ts_str)
        return datetime.fromtimestamp(unix_ts, tz=pytz.UTC)
    except ValueError:
        pass
    return parse_eastern_timestamp(ts_str)


def parse_eastern_timestamp(ts_str: str) -> datetime:
    dt = dateutil_parser.parse(ts_str)
    if dt.tzinfo is None:
        dt = EASTERN.localize(dt)
    return dt.astimezone(pytz.UTC)


def make_text_renderer(msg_id: str, author: str, message: str, timestamp_usec: int) -> dict:
    return {
        'liveChatTextMessageRenderer': {
            'id': msg_id,
            'timestampUsec': str(timestamp_usec),
            'authorName': {'simpleText': author},
            'message': {'runs': [{'text': message}]},
        }
    }


def make_superchat_renderer(msg_id: str, author: str, message: str,
                             timestamp_usec: int, amount: str) -> dict:
    return {
        'liveChatPaidMessageRenderer': {
            'id': msg_id,
            'timestampUsec': str(timestamp_usec),
            'authorName': {'simpleText': author},
            'message': {'runs': [{'text': message}]},
            'purchaseAmountText': {'simpleText': amount},
        }
    }


def make_line(item: dict, offset_ms: int) -> dict:
    return {
        'replayChatItemAction': {
            'actions': [{'addChatItemAction': {'item': item}}],
            'videoOffsetTimeMsec': str(offset_ms),
        },
        'isLiveChat': False,
    }


def convert(csv_path: Path, start_time: datetime, output_path: Path) -> int:
    count = 0
    with open(csv_path, encoding='utf-8', newline='') as csv_file, \
         open(output_path, 'w', encoding='utf-8') as out:

        reader = csv.DictReader(csv_file)
        for i, row in enumerate(reader):
            ts_str = row.get('Timestamp (ET)', '').strip()
            author = row.get('Author', '').strip()
            message = row.get('Message', '').strip()
            msg_type = row.get('Message Type', '').strip()
            superchat_amount = row.get('SuperChat Amount', '').strip()

            # Skip termination reason row written by livechat.py
            if ts_str.startswith('Termination Reason') or not ts_str:
                continue

            try:
                msg_time = parse_eastern_timestamp(ts_str)
            except Exception as e:
                print(f"Warning: could not parse timestamp on row {i+2}: {ts_str!r} ({e})", file=sys.stderr)
                continue

            offset_ms = int((msg_time - start_time).total_seconds() * 1000)
            if offset_ms < 0:
                print(f"Warning: row {i+2} has negative offset ({offset_ms}ms), skipping.", file=sys.stderr)
                continue

            timestamp_usec = int(msg_time.timestamp() * 1_000_000)
            msg_id = f'csv_{i}'

            if msg_type == 'superChatEvent' and superchat_amount:
                item = make_superchat_renderer(msg_id, author, message, timestamp_usec, superchat_amount)
            else:
                item = make_text_renderer(msg_id, author, message, timestamp_usec)

            out.write(json.dumps(make_line(item, offset_ms), ensure_ascii=False) + '\n')
            count += 1

    return count


def get_first_message_time(csv_path: Path) -> Optional[datetime]:
    """Return the timestamp of the first valid message in the CSV."""
    with open(csv_path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_str = row.get('Timestamp (ET)', '').strip()
            if not ts_str or ts_str.startswith('Termination Reason'):
                continue
            try:
                return parse_eastern_timestamp(ts_str)
            except Exception:
                continue
    return None


def get_video_creation_time(video_path: Path) -> Optional[datetime]:
    """Extract creation_time from video file metadata using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(video_path)],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
        creation_time_str = info.get('format', {}).get('tags', {}).get('creation_time')
        if creation_time_str:
            return dateutil_parser.parse(creation_time_str).astimezone(pytz.UTC)
    except FileNotFoundError:
        print("Warning: ffprobe not found. Install ffmpeg to use this feature.", file=sys.stderr)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        pass
    return None


def choose_start_time(video_time: Optional[datetime], first_msg_time: Optional[datetime]) -> datetime:
    """Show both candidate times, their difference, a recommendation, and ask the user to choose."""
    fmt = '%Y-%m-%d %H:%M:%S %Z'

    print("\n--- Stream start time candidates ---")

    if video_time:
        print(f"  [V] Video creation_time : {video_time.astimezone(EASTERN).strftime(fmt)}")
    else:
        print("  [V] Video creation_time : not available")

    if first_msg_time:
        print(f"  [C] First chat message  : {first_msg_time.astimezone(EASTERN).strftime(fmt)}")
    else:
        print("  [C] First chat message  : not available")

    if video_time and first_msg_time:
        diff_seconds = (first_msg_time - video_time).total_seconds()
        if diff_seconds >= 0:
            print(f"\n  First chat message arrived {diff_seconds:.0f}s after video creation_time.")
        else:
            print(f"\n  First chat message is {abs(diff_seconds):.0f}s BEFORE video creation_time.")
            print("  This likely means the video was downloaded after the stream ended,")
            print("  so creation_time reflects the download time, not the stream start.")

    print("\n--- Recommendation ---")
    if video_time and first_msg_time:
        diff_seconds = (first_msg_time - video_time).total_seconds()
        if 0 <= diff_seconds <= 600:
            print("  Use VIDEO creation_time [V].")
            print("  It predates the first chat message by a plausible amount, suggesting")
            print("  the video was downloaded live and creation_time ~ stream start.")
            recommendation = 'v'
        elif diff_seconds < 0:
            print("  Use FIRST CHAT MESSAGE [C].")
            print("  Video creation_time is after the first chat message, so it was likely")
            print("  downloaded after the stream ended. creation_time is not the stream start.")
            recommendation = 'c'
        else:
            print("  Use FIRST CHAT MESSAGE [C] as a conservative estimate.")
            print(f"  The gap ({diff_seconds:.0f}s) is large — creation_time may reflect a download")
            print("  that started well after the stream began.")
            recommendation = 'c'
    elif video_time:
        print("  Use VIDEO creation_time [V] — no chat time available to compare.")
        recommendation = 'v'
    elif first_msg_time:
        print("  Use FIRST CHAT MESSAGE [C] — no video time available.")
        recommendation = 'c'
    else:
        print("  No candidates available. You will need to enter the time manually.")
        return prompt_start_time()

    print()
    choices = []
    if video_time:
        choices.append('v')
    if first_msg_time:
        choices.append('c')
    choices.append('m')
    choice_str = '/'.join(choices) + '/m(manual)'
    prompt = f"Choose [{choice_str}] (default: {recommendation}): "

    while True:
        answer = input(prompt).strip().lower() or recommendation
        if answer == 'v' and video_time:
            print(f"Using video creation_time: {video_time.astimezone(EASTERN).strftime(fmt)}")
            return video_time
        elif answer == 'c' and first_msg_time:
            print(f"Using first chat message: {first_msg_time.astimezone(EASTERN).strftime(fmt)}")
            return first_msg_time
        elif answer == 'm':
            return prompt_start_time()
        else:
            print("Invalid choice, try again.")


def prompt_start_time() -> datetime:
    print("Enter the stream start time (Eastern Time).")
    print("Examples: '2024-01-15 20:00:00' or '2024-01-15 20:00:00 EST'")
    ts_str = input("Stream start time: ").strip()
    return parse_eastern_timestamp(ts_str)


def main():
    ap = argparse.ArgumentParser(description='Convert livechat.py CSV to yt-dlp .live_chat.json')
    ap.add_argument('csv', help='Path to the CSV file from livechat.py')
    ap.add_argument('infojson', nargs='?', help='Path to yt-dlp .info.json (optional)')
    ap.add_argument('--start', help='Stream start time as a string, e.g. "2024-01-15 20:00:00 EST"')
    ap.add_argument('--video', help='Path to the video file (reads creation_time via ffprobe)')
    ap.add_argument('--output', help='Output .live_chat.json path (default: <csv>.live_chat.json)')
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.", file=sys.stderr)
        sys.exit(1)

    # Determine stream start time
    start_time: Optional[datetime] = None

    if args.start:
        start_time = parse_start_time(args.start)
        print(f"Using provided start time: {start_time.astimezone(EASTERN)}")

    elif args.infojson:
        info_path = Path(args.infojson)
        if not info_path.exists():
            print(f"Error: {info_path} not found.", file=sys.stderr)
            sys.exit(1)
        start_time = load_start_time_from_infojson(info_path)
        if start_time:
            print(f"Stream start time from info.json: {start_time.astimezone(EASTERN)}")
        else:
            print("Warning: no release_timestamp or timestamp found in info.json.", file=sys.stderr)

    if start_time is None:
        first_msg_time = get_first_message_time(csv_path)
        video_time = None
        if args.video:
            video_path = Path(args.video)
            if not video_path.exists():
                print(f"Error: {video_path} not found.", file=sys.stderr)
                sys.exit(1)
            video_time = get_video_creation_time(video_path)
            if not video_time:
                print("Warning: could not read creation_time from video file.", file=sys.stderr)

        if video_time or first_msg_time:
            start_time = choose_start_time(video_time, first_msg_time)
        else:
            print("\nCould not determine stream start time automatically.")
            print("If the video was deleted from YouTube, yt-dlp cannot retrieve it.")
            print("Options:")
            print("  1. Re-run with --video to read the video file's creation_time.")
            print("  2. Check the Wayback Machine or web archives for the stream's start time.")
            print("  3. Enter the time manually below.")
            print()
            start_time = prompt_start_time()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Match yt-dlp naming: strip .csv, add .live_chat.json
        stem = csv_path.stem
        output_path = csv_path.with_name(stem + '.live_chat.json')

    print(f"Converting {csv_path} -> {output_path}")
    count = convert(csv_path, start_time, output_path)
    print(f"Done. Wrote {count} messages.")
    print(f"\nTo use with mpv:")
    print(f"  1. Install mpv-youtube-chat: https://github.com/BanchouBoo/mpv-youtube-chat")
    print(f"  2. Rename output to match the video filename (same stem, .live_chat.json extension)")
    print(f"  3. Play the video in mpv — chat loads automatically")


if __name__ == '__main__':
    main()
