# download_comments2.py
# claude.ai
# download youtube comments only
# with progress logger that shows:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Starting comment download for: https://www.youtube.com/watch?v=...
# Downloaded 70/699 comments (10%)
# Downloaded 140/699 comments (20%)
# Downloaded 210/699 comments (30%)
# ...
# Processing 699 comments...
# Writing to CSV: 10%
# Writing to CSV: 20%
# Writing to CSV: 30%
# ...
# Comments successfully saved to VIDEO_ID_comments.csv
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import sys
from yt_dlp import YoutubeDL
import csv
from datetime import datetime
import pytz

class ProgressLogger:
    def __init__(self):
        self.current = 0
        self.total = 0
        self.last_percentage = 0
    
    def progress_hook(self, d):
        if d['status'] == 'downloading_comments':
            self.current = d.get('n_entries', 0)
            self.total = d.get('total_entries') or self.current
            
            # Calculate percentage
            percentage = int((self.current / max(self.total, 1)) * 100)
            
            # Only print when percentage changes by at least 10%
            if percentage >= self.last_percentage + 10 or percentage == 100:
                print(f"Downloaded {self.current}/{self.total} comments ({percentage}%)")
                self.last_percentage = (percentage // 10) * 10

def convert_to_eastern(timestamp):
    """Convert UTC timestamp to Eastern Time"""
    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return utc_time.astimezone(pytz.timezone('US/Eastern'))

def download_comments(url: str) -> str:
    """Download comments from a YouTube video and save them to a CSV file"""
    
    # Create progress logger
    progress = ProgressLogger()
    
    # Configure yt-dlp options
    ydl_opts = {
        'extract_flat': True,  # Do not download video
        'quiet': True,
        'no_warnings': True,
        'getcomments': True,   # Enable comment downloading
        'progress_hooks': [progress.progress_hook]
    }

    try:
        # Create YoutubeDL object
        with YoutubeDL(ydl_opts) as ydl:
            # Extract video information and comments
            print(f"Starting comment download for: {url}")
            info = ydl.extract_info(url, download=False)
            
            if not info.get('comments'):
                print("No comments found or comments are disabled for this video.")
                return
            
            # Create CSV filename from video ID
            csv_filename = f"{info['id']}_comments.csv"
            total_comments = len(info['comments'])
            print(f"\nProcessing {total_comments} comments...")
            
            # Write comments to CSV
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
                        
                        # Show CSV writing progress every 10%
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_comments.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    download_comments(url)