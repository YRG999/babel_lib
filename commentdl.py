# commentdl_updated_v2
# downloads comments from a youtube video and saves as JSON and CSV
# depends on youtube_functions.py

import csv
import sys
from youtube_functions import download_comments, get_video_url, extract_comments_from_json

if __name__ == "__main__":
    video_url = get_video_url()
    if not video_url:
        print("No video URL provided.")
        sys.exit(1)

    comments_file = download_comments(video_url)
    if comments_file:
        print(f"Comments saved to: {comments_file}")
        extracted_data = extract_comments_from_json(comments_file)
        csv_filename = comments_file.replace(".json", ".csv")
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Comment ID', 'Text', 'Author', 'Timestamp', 'Eastern Time'])
            writer.writerows(extracted_data)
        print(f"Comments extracted to: {csv_filename}")
    else:
        print("Failed to download comments.")
