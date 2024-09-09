# youtube_downloader_main2.py

import subprocess
import platform
from dotenv import load_dotenv
from youtube_downloader import YouTubeProcessor as YouTubeDownloader
from youtube_live_chat_fetcher import YouTubeLiveChatFetcher

# Load environment variables from .env file
load_dotenv()

class CombinedYouTubeProcessor:
    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.live_chat_fetcher = YouTubeLiveChatFetcher()

    def open_new_terminal(self, command: str, title: str) -> subprocess.Popen:
        system = platform.system()
        if system == "Windows":
            return subprocess.Popen(f'start cmd.exe /K "title {title} && {command}"', shell=True)
        elif system == "Darwin":  # macOS
            return subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "{command}"'])
        elif system == "Linux":
            return subprocess.Popen(['x-terminal-emulator', '-e', f'bash -c "{command}; exec bash"'])
        else:
            print(f"Unsupported operating system: {system}")
            return None

    def process_live_video(self, video_id: str):
        # Open new terminal for yt-dlp
        yt_dlp_command = f"yt-dlp --live-from-start {video_id}"
        yt_dlp_process = self.open_new_terminal(yt_dlp_command, "YT-DLP Downloader")

        if yt_dlp_process is None:
            print("Failed to start yt-dlp process. Exiting.")
            return

        print("Started yt-dlp in a new window. Beginning live chat fetch in this window.")
        
        # Run live chat fetcher in the current window
        try:
            self.live_chat_fetcher.fetch_live_chat(video_id)
        except KeyboardInterrupt:
            print("\nLive chat fetching interrupted by user.")
        finally:
            print("Live chat fetching ended. Waiting for yt-dlp to finish...")
            yt_dlp_process.wait()
            print("yt-dlp process completed.")

    def process_non_live_video(self, url: str):
        self.downloader.process_video(url)

def get_video_id(url: str) -> str:
    # Extract video ID from URL
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        return url.split("v=")[-1].split("&")[0]
    else:
        return url  # Assume it's already a video ID

def main():
    processor = CombinedYouTubeProcessor()

    url = input("Please enter the full YouTube URL or video ID: ")
    video_id = get_video_id(url)

    is_live = input("Is this a live video? (y/n): ").lower().strip()

    if is_live == 'y':
        print(f"Processing live video: {video_id}")
        print("Opening a separate terminal window for yt-dlp...")
        processor.process_live_video(video_id)
    elif is_live == 'n':
        print(f"Processing non-live video: {url}")
        processor.process_non_live_video(url)
    else:
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()