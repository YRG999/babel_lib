# ytdl_comments.py

from ytdl_updated import *

def download_comments_to_csv():
    '''
    Download comments (info) and convert to csv.
    
    Return raw comments json (info.json) and csv files (info.json.csv).
    '''

    urls = get_video_url()
    download_comments_new([urls])

    comment_files = return_comment_files()
    for file in comment_files:
        comment_csv = comment_to_csv(file)
        print(f"Comments saved as: {comment_csv}")

def main():
    download_comments_to_csv()

if __name__ == "__main__":
    main()