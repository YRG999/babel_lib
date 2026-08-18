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
    """Extract comments from info.json to CSV. Returns the info.json path, or None."""
    info_json_files = glob.glob("*.info.json")
    if info_json_files:
        latest_info_json = max(info_json_files, key=os.path.getctime)
        comments_csv = latest_info_json.replace('.info.json', '_comments.csv')
        extract_comments_to_csv(latest_info_json, comments_csv)
        return latest_info_json
    click.echo("No .info.json file found for comment extraction.", err=True)
    return None

def _is_kick_live_url(url: str) -> bool:
    """Return True if url looks like a Kick channel page (live stream), not a VOD or clip."""
    # Kick live:  kick.com/username
    # Kick VOD:   kick.com/username/videos/UUID
    # Kick clip:  kick.com/username/clips/ID  or  kick.com/username?clip=...
    return bool(re.match(r"https?://(?:www\.)?kick\.com/[^/?#]+/?$", url))

def _is_kick_vod_url(url: str) -> bool:
    """Return True if url looks like a Kick VOD (contains /videos/UUID)."""
    return bool(re.search(r"kick\.com/[^/?#]+/videos/[0-9a-f-]{36}", url, re.IGNORECASE))

def _try_ytdlp(url: str, out_pattern: str) -> bool:
    """Run yt-dlp as a subprocess. Returns True if it exits cleanly."""
    result = subprocess.run(["yt-dlp", "-o", out_pattern, "--", url])
    return result.returncode == 0

def _sabr_ytdlp_path() -> str:
    """Path to the yt-dlp binary in the repo-root venv-sabr virtualenv."""
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    )
    return os.path.join(repo_root, "venv-sabr", "bin", "yt-dlp")

def _download_youtube_sabr(url: str, cookies: bool, comments: bool) -> bool:
    """Download a YouTube video via the SABR dev build of yt-dlp in venv-sabr.

    SABR is YouTube's own streaming protocol; it is not subject to the per-URL
    data cap YouTube applies to regular https media URLs on distrusted IPs
    (e.g. VPN exits). Support comes from the unmerged yt-dlp PR #13515, so it
    lives in a separate virtualenv instead of the pinned stable yt-dlp.
    Returns True if yt-dlp exits cleanly.
    """
    ytdlp = _sabr_ytdlp_path()
    if not os.path.exists(ytdlp):
        raise click.ClickException(
            "--sabr requires the venv-sabr virtualenv at the repo root "
            "(see README 'SABR downloads'). Create it with:\n"
            "  python -m venv venv-sabr\n"
            '  venv-sabr/bin/pip install "yt-dlp[default,curl-cffi] @ '
            'git+https://github.com/yt-dlp/yt-dlp.git@refs/pull/13515/head" '
            "yt-dlp-getpot-wpc\n"
            "Google Chrome must be installed (the wpc token provider drives a "
            "logged-out, throwaway Chrome instance)."
        )
    cmd = [
        ytdlp,
        "--extractor-args", "youtube:formats=duplicate",
        # Prefer SABR formats; fall back to the regular selectors if absent.
        "-f", "bv*[protocol=sabr]+ba[protocol=sabr]/b[protocol=sabr]/bv*+ba/best",
        "--merge-output-format", "mp4",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en,en-US,en-GB,en-AU,live_chat",
        "--write-description", "--write-info-json",
        "-o", "%(title)s.%(ext)s",
    ]
    if cookies:
        cmd += ["--cookies-from-browser", "firefox"]
    if comments:
        cmd.append("--write-comments")
    cmd += ["--", url]
    result = subprocess.run(cmd)
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
@click.option('--comments-only', is_flag=True, default=False,
              help='Download comments only (no video, subtitles, or live chat) '
                   'and extract to CSV. The info JSON is kept.')
@click.option('--video-only', is_flag=True, default=False,
              help='(Kick VOD only) Download video only, skip chat.')
@click.option('--chat-only', is_flag=True, default=False,
              help='(Kick VOD only) Download chat only, skip video.')
@click.option('--chat-delay', default=300, show_default=True,
              help='(Kick VOD only) Delay between chat API requests in milliseconds (min 100).')
@click.option('--sabr', is_flag=True, default=False,
              help='(YouTube full-download mode only) Download via the SABR dev build of '
                   'yt-dlp in venv-sabr. Works around YouTube limiting regular downloads '
                   'to a few hundred KB on distrusted IPs (e.g. VPN exits). Slower: '
                   'YouTube paces SABR delivery.')
def main(url, cookies, comments, metadata_only, transcript_only, comments_only, video_only, chat_only, chat_delay, sabr):
    """Download a YouTube video (or just its metadata/transcript) and convert outputs.

    URL is the full video URL. Always quote it in zsh/bash to prevent
    the shell from interpreting '?' as a glob wildcard:

        python src/main.py "https://www.youtube.com/watch?v=VIDEO_ID"

    For Kick VODs, downloads video and full chat history:

        python src/main.py "https://kick.com/username/videos/UUID"

    For Kick live streams, yt-dlp is tried first. If it fails, the download
    automatically falls back to kick_live_downloader (Playwright + ffmpeg):

        python src/main.py "https://kick.com/username"

    By default, downloads the video, subtitles, description, and info JSON,
    then converts subtitles to text (deduped) and live chat to CSV.
    Comments are not downloaded unless --comments is specified.

    --comments-only skips everything except comments: they are extracted to
    <title>_comments.csv. The .info.json is kept for debugging or
    re-extracting the CSV later.
    """
    if sum([metadata_only, transcript_only, comments_only]) > 1:
        raise click.UsageError(
            "--metadata-only, --transcript-only, and --comments-only are mutually exclusive."
        )

    if sabr and (metadata_only or transcript_only or comments_only):
        raise click.UsageError(
            "--sabr only applies to the full download mode (it exists to get the "
            "video past YouTube's data cap; the *-only modes download no video)."
        )
    if sabr and (_is_kick_vod_url(url) or _is_kick_live_url(url)):
        raise click.UsageError("--sabr is YouTube-only.")

    if _is_kick_vod_url(url):
        click.echo(f"Detected Kick VOD URL: {url}")
        from kick_vod_downloader import main as kick_vod_main
        args = [url]
        if video_only:
            args.append("--video-only")
        if chat_only:
            args.append("--chat-only")
        args += ["--chat-delay", str(chat_delay)]
        kick_vod_main(args, standalone_mode=False)
        return

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
        elif sabr:
            click.echo("Downloading via SABR dev build (venv-sabr)...")
            if not _download_youtube_sabr(url, cookies, comments):
                raise click.ClickException("SABR download failed.")
            convert_transcripts()
            convert_livechat()
            if comments:
                extract_comments()
        else:
            downloader = YouTubeDownloader(
                use_cookies=cookies,
                download_comments=comments,
                metadata_only=metadata_only,
                transcript_only=transcript_only,
                comments_only=comments_only,
            )
            downloader.download_video_info_comments([url])

            if comments_only:
                # Keep the .info.json — useful for debugging and re-extracting the CSV.
                extract_comments()
            else:
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
