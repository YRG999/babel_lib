# youtube_audio_downloader.py

import subprocess

def download_audio_from_youtube(url):
    """Downloads the audio from a YouTube URL using yt-dlp."""
    
    command = f"yt-dlp -f bestaudio {url}"
    subprocess.run(command, shell=True)
    print("Audio download complete!")

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    download_audio_from_youtube(url)
