# youtube_functions

import subprocess
import json
import datetime
import pytz
import re
import csv
import os
import time
from yt_dlp import YoutubeDL
from extract_functions import *

# Get video

def get_video_url():
    return input("Please enter the full YouTube URL: ")

# Get filename

def get_recently_downloaded_filename(extension, current_time):
    '''
    Scan the directory for the most recently downloaded file with the specified extension.
    
    Parameters:
    - extension: The file extension to search for (e.g., 'live_chat.json').
    - current_time: The time marking the start of the download operation.
    
    Returns:
    - The filename of the most recently downloaded file with the specified extension.
    - None if no such file is found.
    '''
    for filename in os.listdir('.'):
        if filename.endswith(extension) and os.path.getctime(filename) > current_time:
            return filename
    return None

# Download video

def download_video(URLS):
    '''
    Download video and return filename.
    '''

    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
    }
    
    with YoutubeDL(ydl_opts_video) as ydl:
        ydl.download(URLS)

    # Retrieve the filename of the recently downloaded video
    video_filename = get_recently_downloaded_filename('.mp4', current_time)
    if video_filename:
        return f"Chat downloaded as: {video_filename}"
    else:
        return "Failed to download chat or extract filename."

# Download chat

def download_chat(URLS):
    '''
    Download chat (as subtitles) and return filename.
    '''
    # Mark the current time. We'll use this to identify newly created files later.
    current_time = time.time()

    ydl_opts_chat = {
        'skip_download': True,          # Don't download the video, just subtitles (live chat replay)
        'writesubtitles': True,         # Write subtitle (live chat) file
    }
    
    with YoutubeDL(ydl_opts_chat) as ydl:
        ydl.download([URLS])

    # Retrieve the filename of the recently downloaded live chat
    chat_filename = get_recently_downloaded_filename('live_chat.json', current_time)
    if chat_filename:
        return f"Chat downloaded as: {chat_filename}"
    else:
        return "Failed to download chat or extract filename."

# Download comments

def download_comments(URLS):
    '''
    Download comments and return filename.
    '''

    ydl_opts_comments = {
        'skip_download': True,          # Don't download the video, just subtitles (live chat replay)
        'getcomments': True,            # Extract video comments; requires writeinfojson to write to disk
        'writeinfojson': True,          # Write the video description to a .info.json file
    }
    
    with YoutubeDL(ydl_opts_comments) as ydl:
        ydl.download(URLS)

    # Retrieve the filename of the recently downloaded comments
    comments_filename = get_recently_downloaded_filename('.en.vtt', current_time)
    if comments_filename:
        return f"Chat downloaded as: {comments_filename}"
    else:
        return "Failed to download chat or extract filename."

# TODO Download metadata

def download_video_info_comments(URLS):
    '''
    Download comments, metadata, and video.
    TODO: Return filenames
    '''
    # ydl_opts = {
    #     'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    #     'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
    #     'getcomments': True,            # Extract video comments; requires writeinfojson to write to disk
    #     'writeinfojson': True,          # Write the video description to a .info.json file
    #     'writesubtitles': True,         # Write subtitle files
    #     'postprocessors': [{
    #         'key': 'FFmpegSubtitlesConvertor',
    #         'format': 'srt',
    #     }],
    # }
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
        'getcomments': True,            # Extract video comments; requires writeinfojson to write to disk
        'writesubtitles': True,
        'writeautomaticsub': True,  # Attempt to write automatic subtitles
        'subtitleslangs': ['en'],   # Assuming English. Adjust as needed.
        'writeinfojson': True,      # Write video metadata to a .json file
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(URLS)

    return "Everything downloaded"

# Download & convert comments

def download_comments2(video_url):
    '''
    Download comments and save to JSON
    '''
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
    comments_file = ""
    for line in result.stdout.split('\n'):
        if line.strip().startswith('[info] Writing video metadata as JSON to:'):
            comments_file = line.split(':')[-1].strip()

    # Read the content of the JSON file and return it
    with open(comments_file, 'r') as file:
        comments_data = file.read()

    # Remove the temporary JSON file
    os.remove(comments_file)

    return comments_data

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

def download_comments_and_return_data(video_url):
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
    comments_file = ""
    for line in result.stdout.split('\n'):
        if line.strip().startswith('[info] Writing video metadata as JSON to:'):
            comments_file = line.split(':')[-1].strip()
            print(f"Comments JSON saved to: {comments_file}")

    # Read the content of the JSON file and return it
    with open(comments_file, 'r') as file:
        comments_data = file.read()

    return comments_data

def process_comments_data(comments_data):
    if comments_data:
        extracted_data = extract_comments_from_json(comments_data)

        # Convert comments to CSV
        csv_filename = "comments_output.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Comment ID', 'Text', 'Author', 'Timestamp', 'Eastern Time'])
            writer.writerows(extracted_data)
        
        print(f"Comments extracted to: {csv_filename}")
    else:
        print("Failed to download comments.")

# Download & clean transcript

def download_transcript(video_url):
    # Use yt-dlp to download transcript from the given video URL
    result = subprocess.run(
        [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--skip-download",
            "--sub-langs", "en",
            video_url
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Extract the name of the transcript file from the output
    for line in result.stdout.split('\n'):
        if line.strip().startswith('[info] Writing video subtitles to:'):
            transcript_file = line.split(':')[-1].strip()
            return transcript_file

def clean_transcript(vtt_filepath):
    # Read the VTT content from the file
    with open(vtt_filepath, "r", encoding="utf-8") as file:
        vtt_content = file.read()

    # Remove lines that look like timecodes and their associated metadata
    cleaned_lines = [line for line in vtt_content.splitlines()
                     if not re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line)
                     and not re.match(r'align:start position:.*%', line)]
    
    # Remove VTT-specific tags
    cleaned_transcript = "\n".join(cleaned_lines)
    cleaned_transcript = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'<c>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'</c>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'&nbsp;', '', cleaned_transcript)

    # Remove duplicate lines
    # Edge case: could delete intentional duplicate lines
    lines_seen = set()
    unique_lines = []
    for line in cleaned_transcript.splitlines():
        if line.strip() and line not in lines_seen:
            lines_seen.add(line)
            unique_lines.append(line)

    cleaned_transcript = "\n".join(unique_lines)

    # Save to a new file
    output_filename = vtt_filepath+"cleanedtranscript.txt"
    # output_filename = "/mnt/data/cleaned_transcript_final.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(cleaned_transcript)

    return output_filename

# Extract live chat & write to CSV

def extract_data_from_json(json_path):
    data_list = []
    
    # Load each JSON object separately, ignoring whitespace between them
    with open(json_path, 'r') as json_file:
        decoder = json.JSONDecoder()
        file_content = json_file.read()
        idx = 0
        while idx < len(file_content):
            try:
                obj, idx = decoder.raw_decode(file_content, idx)
                data_list.append(obj)
            except json.JSONDecodeError:
                idx += 1  # Skip over any whitespace or unexpected characters
    
    # Extract required data
    extracted_data = []
    for data in data_list:
        actions = data.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            item = action.get('addChatItemAction', {}).get('item', {}).get('liveChatTextMessageRenderer', {})
            message = extract_text_and_emoji(item)
            authorname = extract_authorname(item)
            timestamp = extract_timestamp(item)
            eastern_time = convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            extracted_data.append([message, authorname, eastern_time])
    
    return extracted_data

def write_to_csv(data, csv_path):
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Message", "AuthorName", "Eastern Time"])
        writer.writerows(data)

def convert_chat_to_csv(comments_file):
    ## Rename comments JSON file to live_chat JSON file
    old_name = comments_file
    new_name = old_name.replace(".info.json", ".live_chat.json")
    json_path = new_name  # Path to your JSON file

    ## check to see if there is a downloaded livechat JSON file
    if os.path.exists(json_path):
        csv_path = json_path + ".csv"  # Name CSV file by added extension to JSON file
        data = extract_data_from_json(json_path) # Extract data from live_chat.json
        write_to_csv(data, csv_path) # Write to live_chat.json.csv
        print(f"Data written to '{csv_path}'") # Print the name of the CSV file to the console
    else:
        print(f"'{json_path}' does not exist.")
