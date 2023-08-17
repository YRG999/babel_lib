# youtube_functions

import subprocess
import json
import datetime
import pytz

def download_comments(video_url):
    # Use yt-dlp to download comments from the given video URL
    result = subprocess.run(
        [
            'yt-dlp',
            '--skip-download',
            '--write-comments',
            '--no-progress',
            '--no-warnings',
            video_url
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Extract the name of the comments file from the output
    for line in result.stdout.split('\n'):
        if line.strip().startswith('[info] Writing video metadata as JSON to:'):
            comments_file = line.split(':')[-1].strip()
            return comments_file

    return ""  # Return empty string if no file found

def get_video_url():
    return input("Please enter the full YouTube URL: ")

def convert_to_eastern(timestamp):
    # Convert Unix timestamp to naive UTC datetime
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    
    # Make the UTC datetime timezone-aware
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    
    # Convert to Eastern Time
    eastern_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
    
    return eastern_time

def extract_comments_from_json(json_file):
    # 1. Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # 2. Traverse the JSON data
    comments = data['comments']
    extracted_data = []
    for comment in comments:
        comment_id = comment['id']
        text = comment['text']
        author = comment['author']
        timestamp = comment['timestamp']
        eastern_time = convert_to_eastern(timestamp)
        extracted_data.append([comment_id, text, author, timestamp, eastern_time.strftime('%Y-%m-%d %H:%M:%S')])

    return extracted_data
