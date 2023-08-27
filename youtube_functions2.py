# youtube_functions2.py

import csv
import json
from yt_dlp import YoutubeDL
from extract_functions import extract_authorname, extract_timestamp, convert_to_eastern, extract_text_and_emoji

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

def download_chat(URLS):
    ydl_opts_chat = {
        'skip_download': True,          # Don't download the video, just subtitles (live chat replay)
        'allsubs': True,                # Try to download all available subtitles (includes live chat replay)
        'writesubtitles': True,         # Write subtitle files
        'postprocessors': [{
            'key': 'FFmpegSubtitlesConvertor',
            'format': 'srt',
        }],
    }
    
    with YoutubeDL(ydl_opts_chat) as ydl:
        ydl.download(URLS)

def download_video(URLS):
    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
    }
    
    with YoutubeDL(ydl_opts_video) as ydl:
        ydl.download(URLS)
