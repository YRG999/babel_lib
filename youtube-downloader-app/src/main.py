# CLI for downloading YouTube videos, metadata, and transcripts using yt-dlp.
# Converts live chat to CSV and deduplicates transcripts automatically.
# For Kick live streams, tries yt-dlp first and falls back to kick_live_downloader.

import glob
import os
import re
import subprocess
import click
from downloader import YouTubeDownloader
from extract_comments import extract_comments_to_csv
from vtt_to_text import vtt_to_text
from livechat_to_csv import livechat_json_to_csv
from remove_dupe_lines import remove_duplicate_lines

def get_new_output_folder(base_name="output"):
    """Find a new output folder name like output1, output2, ..."""
    i = 1
    while True:
        folder = f"{base_name}{i}"
        if not os.path.exists(folder):
            os.makedirs(folder)
            return folder
        i += 1

def convert_transcripts():
    """Convert all VTT files to text and deduplicate."""
    vtt_files = glob.glob("*.vtt")
    for vtt_file in vtt_files:
        txt_file = vtt_to_text(vtt_file)
        if not txt_file:
            txt_file = os.path.splitext(vtt_file)[0] + ".txt"
        deduped_file = os.path.splitext(txt_file)[0] + "_deduped.txt"
        remove_duplicate_lines(txt_file, deduped_file)


def convert_livechat():
    """Convert all live chat NDJSON files to CSV."""
    livechat_json_files = glob.glob("*.live_chat.json")
    for livechat_file in livechat_json_files:
        csv_file = livechat_file.rsplit('.', 1)[0] + '_livechat.csv'
        livechat_json_to_csv(livechat_file, csv_file)

def extract_comments():
    """Extract comments from info.json to CSV."""
    info_json_files = glob.glob("*.info.json")
    if info_json_files:
        latest_info_json = max(info_json_files, key=os.path.getctime)
        comments_csv = latest_info_json.replace('.info.json', '_comments.csv')
        extract_comments_to_csv(latest_info_json, comments_csv)
    else:
        click.echo("No .info.json file found for comment extraction.", err=True)

def _is_kick_live_url(url: str) -> bool:
    """Return True if url looks like a Kick channel page (live stream), not a VOD or clip."""
    # Kick live:  kick.com/username
    # Kick VOD:   kick.com/username/videos/UUID
    # Kick clip:  kick.com/username/clips/ID  or  kick.com/username?clip=...
    return bool(re.match(r"https?://(?:www\.)?kick\.com/[^/?#]+/?$", url))

def _try_ytdlp(url: str, out_pattern: str) -> bool:
    """Run yt-dlp as a subprocess. Returns True if it exits cleanly."""
    result = subprocess.run(["yt-dlp", "-o", out_pattern, url])
    return result.returncode == 0

def _fallback_kick_live(url: str, out: str) -> bool:
    """Fall back to kick_live_downloader for a Kick live stream."""
    from kick_live_downloader import download_kick_live
    click.echo("yt-dlp failed — falling back to kick_live_downloader (Playwright + ffmpeg)...")
    click.echo("Note: if Cloudflare blocks the headless browser, re-run kick_live_downloader.py directly with --headful.")
    return download_kick_live(page_url=url, out=out)

@click.command()
@click.argument('url')
@click.option('--cookies', is_flag=True, default=False,
              help='Use cookies from Firefox browser.')
@click.option('--comments', is_flag=True, default=False,
              help='Download and extract comments to CSV.')
@click.option('--metadata-only', is_flag=True, default=False,
              help='Skip video download; fetch metadata, subtitles, and live chat, '
                   'then convert transcripts and live chat.')
@click.option('--transcript-only', is_flag=True, default=False,
              help='Download subtitles only and convert to deduplicated text.')
def main(url, cookies, comments, metadata_only, transcript_only):
    """Download a YouTube video (or just its metadata/transcript) and convert outputs.

    URL is the full video URL. Always quote it in zsh/bash to prevent
    the shell from interpreting '?' as a glob wildcard:

        python src/main.py "https://www.youtube.com/watch?v=VIDEO_ID"

    For Kick live streams, yt-dlp is tried first. If it fails, the download
    automatically falls back to kick_live_downloader (Playwright + ffmpeg):

        python src/main.py "https://kick.com/username"

    By default, downloads the video, subtitles, description, and info JSON,
    then converts subtitles to text (deduped) and live chat to CSV.
    Comments are not downloaded unless --comments is specified.
    """
    if metadata_only and transcript_only:
        raise click.UsageError("--metadata-only and --transcript-only are mutually exclusive.")

    output_folder = get_new_output_folder()
    original_cwd = os.getcwd()
    os.chdir(output_folder)

    try:
        if _is_kick_live_url(url):
            # Try yt-dlp first; fall back to Playwright + ffmpeg on failure.
            click.echo(f"Detected Kick live stream URL: {url}")
            click.echo("Attempting download with yt-dlp...")
            success = _try_ytdlp(url, out_pattern="%(title)s.%(ext)s")
            if not success:
                success = _fallback_kick_live(url, out="kick_live.mp4")
            if not success:
                raise click.ClickException(
                    "Both yt-dlp and kick_live_downloader failed. "
                    "Try running kick_live_downloader.py directly with --headful."
                )
        else:
            downloader = YouTubeDownloader(
                use_cookies=cookies,
                download_comments=comments,
                metadata_only=metadata_only,
                transcript_only=transcript_only,
            )
            downloader.download_video_info_comments([url])

            convert_transcripts()
            if not transcript_only:
                convert_livechat()
                if comments:
                    extract_comments()

    finally:
        os.chdir(original_cwd)
        click.echo(f"All output files saved in: {output_folder}")

if __name__ == "__main__":
    main()
