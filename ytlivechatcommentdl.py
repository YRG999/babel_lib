# youtube live video, chat, and comments download
# consolidates ytdlchatvidthreads, main_extraction and commentdl
# and uses extract_functions and youtube_functions

import os
import csv
import sys
import threading
from youtube_functions import (
    download_comments, 
    get_video_url, 
    extract_comments_from_json, 
    extract_data_from_json, 
    write_to_csv, 
    download_chat, 
    download_video)

if __name__ == "__main__":
    video_url = get_video_url()
    if not video_url:
        print("No video URL provided.")
        sys.exit(1)

    comments_file = download_comments(video_url)
    if comments_file:
        print(f"Comments saved to: {comments_file}")
        extracted_data = extract_comments_from_json(comments_file)

        # Convert comments to CSV
        
        csv_filename = comments_file.replace(".json", ".csv")
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Comment ID', 'Text', 'Author', 'Timestamp', 'Eastern Time'])
            writer.writerows(extracted_data)
        print(f"Comments extracted to: {csv_filename}")
    else:
        print("Failed to download comments.")

# Download YouTube Live in two threads: chat & video.
## TODO: Debug. This doesn't seem to work as when I disable the `video_thread`, it still downloads the video.
vidurl = video_url
URLS = [vidurl]

# Create threads
video_thread = threading.Thread(target=download_video(URLS))
chat_thread = threading.Thread(target=download_chat(URLS))

# Start threads
video_thread.start()
chat_thread.start()

# Wait for threads to complete
video_thread.join()
chat_thread.join()

# Convert chat JSON to CSV
## This code uses the name of the comments json file to figure out the name of the live chat file
## TODO: figure out how to directly capture the livechat filename (this seems more complex, so used this shortcut instead)

## Rename comments JSON file to live_chat JSON file
old_name = comments_file
new_name = old_name.replace(".info.json", ".live_chat.json")
json_path = new_name  # Path to your JSON file

## check to see if there is a downloaded livechat JSON file
if os.path.exists(json_path):
    csv_path = json_path+".csv"  # Name CSV file by added extension to JSON file
    data = extract_data_from_json(json_path) # Extract data from live_chat.json
    write_to_csv(data, csv_path) # Write to live_chat.json.csv
    print(f"Data written to '{csv_path}'") # Print the name of the CSV file to the console
else:
    print(f"'{json_path}' does not exist.")
