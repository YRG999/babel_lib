# This script downloads YouTube video information, comments, and live chat, and processes them into
# CSV and text formats. It handles cookies, allows for comments-only downloads, and organizes output
# into a new folder each time it runs.

import glob
import os
import shutil
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

def move_file_to_folder(filepath, folder):
    if os.path.exists(filepath):
        shutil.move(filepath, os.path.join(folder, os.path.basename(filepath)))

def main():
    url = input("Please enter the full YouTube URL: ")
    use_cookies = input("Do you want to use cookies from your browser? (y/n): ").strip().lower() == 'y'
    download_comments = input("Do you want to download comments? (y/n): ").strip().lower() == 'y'
    comments_only = input("Do you want to ONLY download comments (no video)? (y/n): ").strip().lower() == 'y'

    # Create output folder before any downloads
    output_folder = get_new_output_folder()

    # Change working directory for all output
    original_cwd = os.getcwd()
    os.chdir(output_folder)

    try:
        downloader = YouTubeDownloader(
            use_cookies=use_cookies,
            download_comments=download_comments,
            comments_only=comments_only
        )
        downloader.download_video_info_comments([url])

        # Comments CSV
        if download_comments or comments_only:
            # More efficient: use os.scandir instead of glob + max with getctime
            latest_info_json = None
            latest_time = 0
            for entry in os.scandir('.'):
                if entry.is_file() and entry.name.endswith('.info.json'):
                    entry_time = entry.stat().st_ctime
                    if entry_time > latest_time:
                        latest_time = entry_time
                        latest_info_json = entry.name
            
            if latest_info_json:
                comments_csv = latest_info_json.replace('.info.json', '_comments.csv')
                extract_comments_to_csv(latest_info_json, comments_csv)
            else:
                print("No .info.json file found. Please check your download.")

        # VTT to text
        vtt_files = glob.glob("*.vtt")
        for vtt_file in vtt_files:
            txt_file = vtt_to_text(vtt_file)
            # If vtt_to_text returns the txt filename, use it; otherwise, construct it:
            if not txt_file:
                txt_file = os.path.splitext(vtt_file)[0] + ".txt"
            deduped_file = os.path.splitext(txt_file)[0] + "_deduped.txt"
            remove_duplicate_lines(txt_file, deduped_file)

        # Live chat NDJSON to CSV
        livechat_json_files = glob.glob("*.live_chat.json")
        for livechat_file in livechat_json_files:
            csv_file = livechat_file.rsplit('.', 1)[0] + '_livechat.csv'
            livechat_json_to_csv(livechat_file, csv_file)

    finally:
        # Return to original directory
        os.chdir(original_cwd)
        print(f"All output files are saved in: {output_folder}")

if __name__ == "__main__":
    main()