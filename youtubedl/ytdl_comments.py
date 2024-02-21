# ytdl_comments.py

from ytdl_updated import *

def download_comments_to_csv():
    # Download comments & convert to CSV.
    urls = get_video_url()
    comment_file = download_comments_new([urls])
    comment_csv = comment_to_csv(comment_file)
    print(f"Comments saved as: {comment_csv}")

def main():
    download_comments_to_csv()

if __name__ == "__main__":
    main()