# youtube_downloader5.py
# claude.ai
# no comments
# to download comments, run 
# `python comments.py "https://www.youtube.com/watch?v=VIDEO_ID"`
# see updated version: youtube_downloader6.py

import json
import csv
import re
from typing import List, Dict, Any
from datetime import datetime
import pytz
import logging
from yt_dlp import YoutubeDL
from extract_functions import extract_text_and_emoji, extract_timestamp

class YouTubeDownloader:
    def __init__(self):
        self.filenames = []

    def download_video_info_comments(self, urls: List[str]) -> List[str]:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en','live_chat'],
            'writedescription': True,
            'writeinfojson': True,
            'progress_hooks': [self._progress_hook],
            'cookiesfrombrowser': ('firefox',)  # Use Firefox cookies
        }

        with YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                ydl.download(url)

        return self.filenames

    def _progress_hook(self, d):
        if d['status'] == 'finished':
            self.filenames.append(d['filename'])

class YouTubeProcessor:
    def __init__(self, cookies_file: str = None):
        self.downloader = YouTubeDownloader()
        self.chat_processor = ChatProcessor()
        self.transcript_processor = TranscriptProcessor()

    def process_video(self, url: str):
        filenames = self.downloader.download_video_info_comments([url])

        for file in filenames:
            if file.endswith(".en.vtt"):
                clean_filename = self.transcript_processor.clean_transcript(file)
                print(f"Transcript saved as: {clean_filename}")
            elif file.endswith(".live_chat.json"):
                output_filename = self.chat_processor.process_chat(file)
                print(f"Live chat saved as: {output_filename}")

class ChatProcessor:
    def process_chat(self, filename: str) -> str:
        json_data = self._load_json_data(filename)
        extracted_data = self._extract_data_from_json(json_data)
        output_filename = filename + "_extracted.csv"
        self._save_to_csv(extracted_data, output_filename)
        return output_filename

    def _load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        try:
            with open(filename, "r") as f:
                return [json.loads(line.strip()) for line in f]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error processing file {filename}: {e}")
            return []

    def _extract_data_from_json(self, json_data: List[Dict[str, Any]]) -> List[List[str]]:
        extracted_data = []
        for data in json_data:
            actions = data.get('replayChatItemAction', {}).get('actions', [])
            for action in actions:
                item = action.get('addChatItemAction', {}).get('item', {})
                chat_renderer = item.get('liveChatTextMessageRenderer') or item.get('liveChatPaidMessageRenderer')
                if chat_renderer:
                    message, authorname, timestamp = self._extract_chat_info(chat_renderer)
                    extracted_data.append([message, authorname, timestamp])
        return extracted_data

    def _extract_chat_info(self, chat_renderer: Dict[str, Any]) -> tuple[str, str, str]:
        authorname = chat_renderer.get('authorName', {}).get('simpleText', '')
        message = extract_text_and_emoji(chat_renderer)
        if 'purchaseAmountText' in chat_renderer:
            purchase_amount = chat_renderer['purchaseAmountText']['simpleText']
            message = f"[Superchat {purchase_amount}] " + message
        timestamp = extract_timestamp(chat_renderer)
        eastern_time = convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return message, authorname, eastern_time

    def _save_to_csv(self, data: List[List[str]], output_filename: str):
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Message', 'Author', 'Timestamp'])
            csv_writer.writerows(data)

class TranscriptProcessor:
    def clean_transcript(self, vtt_filepath: str) -> str:
        with open(vtt_filepath, "r", encoding="utf-8") as file:
            vtt_content = file.read()

        cleaned_lines = self._filter_lines(vtt_content)
        cleaned_transcript = self._clean_content("\n".join(cleaned_lines))
        unique_lines = self._remove_duplicates(cleaned_transcript)

        output_filename = vtt_filepath + "cleanedtranscript.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(unique_lines))

        return output_filename

    def _filter_lines(self, content: str) -> List[str]:
        return [line for line in content.splitlines()
                if not re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line)
                and not re.match(r'align:start position:.*%', line)]

    def _clean_content(self, content: str) -> str:
        content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', content)
        content = re.sub(r'</?c>', '', content)
        return re.sub(r'&nbsp;', '', content)

    def _remove_duplicates(self, content: str) -> List[str]:
        lines_seen = set()
        return [line for line in content.splitlines()
                if line.strip() and line not in lines_seen and not lines_seen.add(line)]

def convert_to_eastern(timestamp: float) -> datetime:
    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return utc_time.astimezone(pytz.timezone('US/Eastern'))

def main():
    processor = YouTubeProcessor()
    url = input("Please enter the full YouTube URL: ")
    processor.process_video(url)

if __name__ == "__main__":
    main()