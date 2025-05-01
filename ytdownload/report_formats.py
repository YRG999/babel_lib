# report_formats.py
# This script uses yt-dlp to report all available formats for a given YouTube video URL.
# It lists the formats without downloading the video.
# Usage: python report_formats.py

from yt_dlp import YoutubeDL

def report_formats(video_url: str):
    ydl_opts = {
        'listformats': True,  # Option to list all available formats
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=False)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    url = input("Enter the YouTube video URL: ")
    report_formats(url)

if __name__ == "__main__":
    main()

# To download a specific format:
# yt-dlp -f "136+bestaudio" "https://www.youtube.com/watch?v=VIDEO_ID"
# Explanation of Format ID
# 136: The format ID for 720p video (video-only).
# bestaudio: Downloads the best available audio stream.
# 136+bestaudio: Combines the specified video format (136) with the best audio.