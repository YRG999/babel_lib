# ytdl_comments.py

from ytdl_updated import *

if __name__ == "__main__":
    # Download comments & convert to CSV.

    urls = get_video_url()
    comment_file = download_comments_new([urls])
    comment_csv = comment_to_csv(comment_file)
    print(f"Comments saved as: {comment_csv}")
