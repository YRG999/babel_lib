# Downloads a Kick.com VOD video and its full chat history to CSV + NDJSON.
# Chat is fetched via time-windowed polling of the Kick chat history API.

import csv
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta

import click
import requests

KICK_VIDEO_API = "https://kick.com/api/v1/video/{uuid}"
KICK_CHAT_API = "https://web.kick.com/api/v1/chat/{channel_id}/history"
CHAT_WINDOW_SECS = 5
DEFAULT_CHAT_DELAY_MS = 300
REQUEST_TIMEOUT = 30
MAX_RETRIES = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def parse_vod_uuid(url: str) -> str:
    m = re.search(r"/videos/([0-9a-f-]{36})", url)
    if not m:
        raise click.BadParameter(f"Could not find a VOD UUID in URL: {url}")
    return m.group(1)


def fetch_with_retry(url: str, params: dict | None = None) -> dict:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                click.echo(f"  Rate limited — waiting {wait}s...", err=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise click.ClickException(f"Request failed after {MAX_RETRIES} attempts: {e}")
            time.sleep(min(2 ** attempt, 8))
    return {}


def parse_kick_datetime(s: str) -> datetime:
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
    ):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise click.ClickException(f"Could not parse Kick datetime: {s!r}")


def extract_message_row(msg: dict) -> dict:
    sender = msg.get("sender") or {}
    identity = sender.get("identity") or {}
    badges = identity.get("badges") or []
    badge_types = ", ".join(b["type"] for b in badges if b.get("type"))

    created_at = msg.get("created_at", "")
    try:
        dt = parse_kick_datetime(created_at)
        created_at = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (click.ClickException, ValueError):
        pass

    metadata_raw = msg.get("metadata")
    amount = ""
    if metadata_raw:
        if isinstance(metadata_raw, str):
            try:
                metadata_raw = json.loads(metadata_raw)
            except (json.JSONDecodeError, TypeError):
                pass
        if isinstance(metadata_raw, dict):
            amount = str(metadata_raw.get("amount") or metadata_raw.get("value") or "")

    return {
        "timestamp": created_at,
        "username": sender.get("username", ""),
        "user_id": sender.get("id", ""),
        "message": msg.get("content", ""),
        "type": msg.get("type", ""),
        "badges": badge_types,
        "color": identity.get("color", ""),
        "amount": amount,
        "message_id": msg.get("id", ""),
        "metadata": json.dumps(msg.get("metadata")) if msg.get("metadata") else "",
    }


def download_chat(channel_id: int, start_dt: datetime, duration_secs: int,
                  output_base: str, chat_delay_ms: int):
    end_dt = start_dt + timedelta(seconds=duration_secs)
    total_windows = (duration_secs + CHAT_WINDOW_SECS - 1) // CHAT_WINDOW_SECS
    current = start_dt
    seen_ids: set = set()
    all_messages: list = []

    click.echo(f"Fetching chat: {start_dt.isoformat()} → {end_dt.isoformat()}")
    click.echo(f"  ~{total_windows} windows ({CHAT_WINDOW_SECS}s each, {chat_delay_ms}ms delay)")

    window_num = 0
    while current < end_dt:
        window_num += 1
        if window_num % 60 == 0:
            pct = (current - start_dt).total_seconds() / duration_secs * 100
            click.echo(f"  {pct:.0f}% — window {window_num}/{total_windows}, {len(all_messages)} messages so far")

        time.sleep(chat_delay_ms / 1000.0)

        ts = current.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        url = KICK_CHAT_API.format(channel_id=channel_id)
        try:
            data = fetch_with_retry(url, params={"start_time": ts})
            messages = (data.get("data") or {}).get("messages") or []
            for msg in messages:
                msg_id = msg.get("id")
                if msg_id and msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    all_messages.append(msg)
        except click.ClickException as e:
            click.echo(f"  Warning: skipping window {ts}: {e}", err=True)

        current += timedelta(seconds=CHAT_WINDOW_SECS)

    all_messages.sort(key=lambda m: m.get("created_at", ""))
    click.echo(f"  Collected {len(all_messages)} unique messages.")

    ndjson_path = output_base + "_chat.ndjson"
    with open(ndjson_path, "w", encoding="utf-8") as f:
        for msg in all_messages:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    click.echo(f"  Raw NDJSON: {ndjson_path}")

    csv_path = output_base + "_chat.csv"
    fieldnames = ["vod_offset", "timestamp", "username", "user_id", "message", "type",
                  "badges", "color", "amount", "message_id", "metadata"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for msg in all_messages:
            row = extract_message_row(msg)
            try:
                msg_dt = parse_kick_datetime(msg.get("created_at", ""))
                offset_secs = int((msg_dt - start_dt).total_seconds())
                h, rem = divmod(max(offset_secs, 0), 3600)
                m, s = divmod(rem, 60)
                row["vod_offset"] = f"{h}:{m:02}:{s:02}"
            except (click.ClickException, ValueError):
                row["vod_offset"] = ""
            writer.writerow(row)
    click.echo(f"  Chat CSV:   {csv_path}")


def get_new_output_folder(base_name="kick_output"):
    i = 1
    while True:
        folder = f"{base_name}{i}"
        if not os.path.exists(folder):
            os.makedirs(folder)
            return folder
        i += 1


@click.command()
@click.argument("url")
@click.option("--video-only", is_flag=True, default=False,
              help="Download video only, skip chat.")
@click.option("--chat-only", is_flag=True, default=False,
              help="Download chat only, skip video.")
@click.option("--chat-delay", default=DEFAULT_CHAT_DELAY_MS, show_default=True,
              help="Delay between chat API requests in milliseconds (min 100).")
def main(url, video_only, chat_only, chat_delay):
    """Download a Kick.com VOD and its full chat history.

    URL must be a Kick VOD URL containing a UUID:

        python src/kick_vod_downloader.py "https://kick.com/username/videos/UUID"

    Outputs to a new kick_outputN/ folder:
      - metadata.json        Raw VOD metadata from Kick API
      - <title>_chat.ndjson  Raw chat messages (one JSON object per line)
      - <title>_chat.csv     Chat in CSV (timestamp, username, message, type, badges, ...)
      - <title>.mp4          Video (unless --chat-only)
    """
    if video_only and chat_only:
        raise click.UsageError("--video-only and --chat-only are mutually exclusive.")

    chat_delay = max(100, chat_delay)

    uuid = parse_vod_uuid(url)
    click.echo(f"VOD UUID: {uuid}")

    click.echo("Fetching VOD metadata...")
    meta = fetch_with_retry(KICK_VIDEO_API.format(uuid=uuid))

    # The /api/v1/video/{uuid} response nests stream data under "livestream".
    livestream = meta.get("livestream") or {}
    title = livestream.get("session_title") or meta.get("session_title") or meta.get("title") or uuid
    channel = livestream.get("channel") or meta.get("channel") or {}
    channel_username = channel.get("slug") or channel.get("username") or "unknown"
    channel_id = livestream.get("channel_id") or meta.get("channel_id") or channel.get("id")
    start_time_str = livestream.get("start_time") or meta.get("start_time", "")
    duration_raw = livestream.get("duration") or meta.get("duration", 0) or 0

    click.echo(f"  Title:    {title}")
    click.echo(f"  Channel:  {channel_username}  (id={channel_id})")
    click.echo(f"  Start:    {start_time_str}")
    click.echo(f"  Duration: {duration_raw} (raw)")

    if not channel_id and not video_only:
        raise click.ClickException("Could not determine channel_id from VOD metadata.")

    # Kick's duration field unit varies — if value looks like milliseconds (> 3 days
    # worth of seconds), convert to seconds.
    duration_secs = int(duration_raw)
    if duration_secs > 86400 * 3:
        duration_secs = duration_secs // 1000
        click.echo(f"  Duration: {duration_secs}s (converted from ms)")
    else:
        click.echo(f"  Duration: {duration_secs}s")

    output_folder = get_new_output_folder()
    safe_title = re.sub(r"[^\w\- ]", "_", f"{channel_username}_{title}")[:80].strip()
    original_cwd = os.getcwd()
    os.chdir(output_folder)

    try:
        with open("metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        click.echo(f"  Metadata: {output_folder}/metadata.json")

        if not chat_only:
            click.echo("\nDownloading video via yt-dlp...")
            result = subprocess.run(["yt-dlp", "-o", f"{safe_title}.%(ext)s", url])
            if result.returncode != 0:
                raise click.ClickException("yt-dlp failed (see output above).")

        if not video_only:
            if not start_time_str:
                raise click.ClickException("start_time missing from VOD metadata — cannot download chat.")
            if duration_secs <= 0:
                raise click.ClickException("VOD duration is zero or missing — cannot download chat.")

            start_dt = parse_kick_datetime(start_time_str)
            click.echo("")
            assert channel_id is not None
            download_chat(
                channel_id=int(channel_id),
                start_dt=start_dt,
                duration_secs=duration_secs,
                output_base=safe_title,
                chat_delay_ms=chat_delay,
            )

    finally:
        os.chdir(original_cwd)
        click.echo(f"\nAll output saved in: {output_folder}/")


if __name__ == "__main__":
    main()
