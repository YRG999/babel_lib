# **Replaced by ytdl_updated.py**
# Download YouTube Live in two threads: chat & video.

from yt_dlp import YoutubeDL
import threading

vidurl = input("Enter livestream URL to download video & chat\n")
URLS = [vidurl]

# URLS = ['https://www.youtube.com/watch?v=livestream-url']

def download_video():
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
    }
    
    with YoutubeDL(ydl_opts_video) as ydl:
        ydl.download(URLS)

def download_chat():
    ydl_opts_chat = {
        'skip_download': True,          # Don't download the video, just subtitles (live chat replay)
        'allsubs': True,                # Try to download all available subtitles (includes live chat replay)
        'writesubtitles': True,         # Write subtitle files
        'postprocessors': [{
            'key': 'FFmpegSubtitlesConvertor',
            'format': 'srt',
        }],
    }
    
    with YoutubeDL(ydl_opts_chat) as ydl:
        ydl.download(URLS)

def download_threads():
    # Create threads
    video_thread = threading.Thread(target=download_video)
    chat_thread = threading.Thread(target=download_chat)

    # Start threads
    video_thread.start()
    chat_thread.start()

    # Wait for both threads to complete
    video_thread.join()
    chat_thread.join()

def main():
    download_threads()

if __name__ == "__main__":
    main()