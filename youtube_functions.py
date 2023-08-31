# youtube_functions

import subprocess
import json
import datetime
import pytz
import re

# Get video

def get_video_url():
    return input("Please enter the full YouTube URL: ")

# Download & convert comments

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

def clean_transcript(vtt_content):
    with open(vtt_content, 'r') as transcript_file:
        file_content = transcript_file.read()

    # Remove lines that look like timecodes
    cleaned_lines = [line for line in file_content.splitlines() 
                     if not re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line)]
    
    # Remove VTT-specific tags
    cleaned_transcript = "\n".join(cleaned_lines)
    cleaned_transcript = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'<c>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'</c>', '', cleaned_transcript)
    cleaned_transcript = re.sub(r'&nbsp;', '', cleaned_transcript)
    
    # Remove empty lines and repeated lines
    lines_seen = set()
    unique_lines = []
    for line in cleaned_transcript.splitlines():
        if line.strip() and line not in lines_seen:
            lines_seen.add(line)
            unique_lines.append(line)
    
    cleaned_transcript = "\n".join(unique_lines)
    
    # Save to a new file
    output_filename = vtt_content+"cleanedtranscript.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(cleaned_transcript)
    
    return output_filename