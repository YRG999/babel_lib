# ytdl_comments.py

from yt_dlp import YoutubeDL
from ytdl_updated import *
from youtube_functions import *
from extract_functions import *

if __name__ == "__main__":
    # Download comments & convert to CSV.

    urls = get_video_url()
    comment_file = download_comments_new([urls])
    # or comment above & uncomment below if you already have comments saved to a json file
    # comment_file = input("filename? ")

    comment_csv = comment_to_csv(comment_file)
    print(f"Comments saved as: {comment_csv}")
