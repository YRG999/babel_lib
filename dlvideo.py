# Download video
# From TikTok, TickTok live, YouTube, YouTube live (without live chat), Apple Trailers, and possibly more, enter the URL to see!

from yt_dlp import YoutubeDL

vidurl = input("URL to download (YT vid or live (no chat), TikTok vid or live, Apple Trailer)\n")
URLS = [vidurl]

ydl_opts = {
    'format': 'bestvideo+bestaudio/best', # download best video
    'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
}

with YoutubeDL(ydl_opts) as ydl:
    ydl.download(URLS)
