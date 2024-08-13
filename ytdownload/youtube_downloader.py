# youtube_downloader_new3.py

from yt_dlp import YoutubeDL
from typing import List, Dict, Any, Optional
import os
import json
import csv
import re  # Add this import
from datetime import datetime
import pytz
from extract_functions import *
import emoji
import logging

class YouTubeDownloader:
    def __init__(self):
        self.filenames = []

    def progress_hook(self, d):
        if d['status'] == 'finished':
            self.filenames.append(d['filename'])

    def download_video_info_comments(self, urls: List[str]) -> List[str]:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'getcomments': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en','live_chat'],
            'writedescription': True,
            'writeinfojson': True,
            'progress_hooks': [self.progress_hook]
        }

        with YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                ydl.download(url)

        return self.filenames

    @staticmethod
    def return_files_with_extension(filenames: List[str], extension: str) -> List[str]:
        return [file for file in filenames if file.endswith(extension)]

    @staticmethod
    def get_file_with_extension(extension: str) -> Optional[str]:
        for filename in os.listdir('.'):
            if filename.endswith(extension):
                return filename
        return None

    @staticmethod
    def convert_to_eastern(timestamp: float) -> datetime:
        utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        return utc_time.astimezone(pytz.timezone('US/Eastern'))

class CommentProcessor:
    @staticmethod
    def comment_to_csv(comment_file: str) -> str:
        with open(comment_file, 'r') as file:
            data = json.load(file)

        comments = data['comments']
        extracted_data = []
        for comment in comments:
            comment_id = comment['id']
            text = comment['text']
            author = comment['author']
            timestamp = comment['timestamp']
            eastern_time = YouTubeDownloader.convert_to_eastern(timestamp)
            extracted_data.append([comment_id, text, author, timestamp, eastern_time.strftime('%Y-%m-%d %H:%M:%S')])

        comment_csv = comment_file + ".csv"
        with open(comment_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Comment ID', 'Text', 'Author', 'Timestamp', 'Eastern Time'])
            writer.writerows(extracted_data)

        return comment_csv

class ChatExtractor:
    @staticmethod
    def is_emoji(text: str) -> bool:
        return emoji.is_emoji(text)

    @staticmethod
    def get_json_data(filename: str = None) -> tuple[List[Dict[str, Any]], str]:
        if filename is None:
            filename = input("Enter the name of the JSON file: ")
        
        try:
            with open(filename, "r") as f:
                data_list = [json.loads(line.strip()) for line in f]
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON in file {filename}: {e}")
            return [], filename
        except FileNotFoundError:
            logging.error(f"File not found: {filename}")
            return [], filename
        
        return data_list, filename

    @staticmethod
    def extract_data_from_json(json_data: List[Dict[str, Any]], json_path: str = None) -> List[List[str]]:
        extracted_data = []
        for data in json_data:
            actions = data.get('replayChatItemAction', {}).get('actions', [])
            for action in actions:
                item = action.get('addChatItemAction', {}).get('item', {})
                
                text_renderer = item.get('liveChatTextMessageRenderer')
                paid_renderer = item.get('liveChatPaidMessageRenderer')
                
                if text_renderer or paid_renderer:
                    chat_renderer = text_renderer or paid_renderer
                    authorname = chat_renderer.get('authorName', {}).get('simpleText', '')
                    message = extract_text_and_emoji(chat_renderer)
                    
                    if paid_renderer:
                        purchase_amount = paid_renderer.get('purchaseAmountText', {}).get('simpleText', '')
                        message = f"[Superchat {purchase_amount}] " + message
                    
                    timestamp = extract_timestamp(chat_renderer)
                    eastern_time = YouTubeDownloader.convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    extracted_data.append([message, authorname, eastern_time])
        
        return extracted_data

    @staticmethod
    def save_to_csv(data: List[List[str]], output_filename: str):
        if not output_filename.lower().endswith('.csv'):
            output_filename += '.csv'
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, output_filename)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Message', 'Author', 'Timestamp'])
            csv_writer.writerows(data)
        
        print(f"Data saved to {output_path}")

class TranscriptProcessor:
    @staticmethod
    def clean_transcript(vtt_filepath: str) -> str:
        with open(vtt_filepath, "r", encoding="utf-8") as file:
            vtt_content = file.read()

        cleaned_lines = [line for line in vtt_content.splitlines()
                         if not re.match(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line)
                         and not re.match(r'align:start position:.*%', line)]

        cleaned_transcript = "\n".join(cleaned_lines)
        cleaned_transcript = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', cleaned_transcript)
        cleaned_transcript = re.sub(r'<c>', '', cleaned_transcript)
        cleaned_transcript = re.sub(r'</c>', '', cleaned_transcript)
        cleaned_transcript = re.sub(r'&nbsp;', '', cleaned_transcript)

        lines_seen = set()
        unique_lines = []
        for line in cleaned_transcript.splitlines():
            if line.strip() and line not in lines_seen:
                lines_seen.add(line)
                unique_lines.append(line)

        cleaned_transcript = "\n".join(unique_lines)

        output_filename = vtt_filepath + "cleanedtranscript.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(cleaned_transcript)

        return output_filename

class YouTubeProcessor:
    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.chat_extractor = ChatExtractor()
        self.comment_processor = CommentProcessor()
        self.transcript_processor = TranscriptProcessor()

    def process_youtube_video(self, url: str):
        filenames = self.downloader.download_video_info_comments([url])

        transcript_files = self.downloader.return_files_with_extension(filenames, ".en.vtt")
        for file in transcript_files:
            clean_filename = self.transcript_processor.clean_transcript(file)
            print(f"Transcript saved as: {clean_filename}")

        livechat_files = self.downloader.return_files_with_extension(filenames, ".live_chat.json")
        for file in livechat_files:
            json_data, _ = self.chat_extractor.get_json_data(file)
            extracted_data = self.chat_extractor.extract_data_from_json(json_data, file)
            output_filename = file + "_extracted.csv"
            self.chat_extractor.save_to_csv(extracted_data, output_filename)
            print(f"Live chat saved as: {output_filename}")

        comment_files = [self.downloader.get_file_with_extension('.info.json')]
        for file in comment_files:
            if file:
                comment_csv = self.comment_processor.comment_to_csv(file)
                print(f"Comments saved as: {comment_csv}")

def main():
    processor = YouTubeProcessor()
    url = input("Please enter the full YouTube URL: ")
    processor.process_youtube_video(url)

if __name__ == "__main__":
    main()
