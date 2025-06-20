# filepath: /youtube-downloader-app/youtube-downloader-app/src/comments.py

import csv
from datetime import datetime
import pytz
from yt_dlp import YoutubeDL
from extract_comments import convert_to_eastern

class ProgressLogger:
    def __init__(self):
        self.current = 0
        self.total = 0
        self.last_percentage = 0
    
    def progress_hook(self, d):
        if d['status'] == 'downloading_comments':
            self.current = d.get('n_entries', 0)
            self.total = d.get('total_entries') or self.current
            
            percentage = int((self.current / max(self.total, 1)) * 100)
            
            if percentage >= self.last_percentage + 10 or percentage == 100:
                print(f"Downloaded {self.current}/{self.total} comments ({percentage}%)")
                self.last_percentage = (percentage // 10) * 10

# def convert_to_eastern(timestamp):
#     utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
#     return utc_time.astimezone(pytz.timezone('US/Eastern'))

def download_comments(url: str, use_cookies: bool) -> str:
    progress = ProgressLogger()
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'getcomments': True,
        'progress_hooks': [progress.progress_hook],
        'cookiesfrombrowser': ('firefox',) if use_cookies else None
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Starting comment download for: {url}")
            info = ydl.extract_info(url, download=False)
            
            if not info.get('comments'):
                print("No comments found or comments are disabled for this video.")
                return
            
            csv_filename = f"{info['id']}_comments.csv"
            total_comments = len(info['comments'])
            print(f"\nProcessing {total_comments} comments...")
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Comment ID', 'Author', 'Text', 'Timestamp', 'Eastern Time', 'Likes'])
                
                for i, comment in enumerate(info['comments'], 1):
                    try:
                        timestamp = comment.get('timestamp', 0)
                        eastern_time = convert_to_eastern(timestamp)
                        
                        writer.writerow([
                            comment.get('id', ''),
                            comment.get('author', ''),
                            comment.get('text', ''),
                            timestamp,
                            eastern_time.strftime('%Y-%m-%d %H:%M:%S'),
                            comment.get('like_count', 0)
                        ])
                        
                        percentage = (i / total_comments) * 100
                        if percentage % 10 == 0:
                            print(f"Writing to CSV: {int(percentage)}%")
                            
                    except Exception as e:
                        print(f"Error processing comment: {e}")
                        continue
            
            print(f"\nComments successfully saved to {csv_filename}")
            return csv_filename

    except Exception as e:
        print(f"An error occurred: {e}")
        return None