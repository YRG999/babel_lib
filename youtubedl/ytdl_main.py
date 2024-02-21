# **Replaced by ytdl_updated.py**

import sys
import threading
from youtube_functions import *

def download_youtube_data(video_url=None):
    if not video_url:
        video_url = get_video_url()
    
    if not video_url:
        print("No video URL provided.")
        sys.exit(1)    

    # Download comments and get the JSON data
    comments_data = download_comments_and_return_data(video_url)
    
    # Process the returned JSON comments data
    process_comments_data(comments_data)

    # Download YouTube Live video and chat in threads

    ## Create threads
    video_thread = threading.Thread(target=download_video, args=(video_url,))
    chat_thread = threading.Thread(target=download_chat, args=(video_url,))

    ## Start threads
    video_thread.start()
    chat_thread.start()

    ## Wait for threads to complete
    video_thread.join()
    chat_thread.join()

if __name__ == "__main__":
    download_youtube_data()
