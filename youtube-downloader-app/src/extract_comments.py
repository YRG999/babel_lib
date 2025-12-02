# extract_comments2.py
# This script extracts comments from a YouTube video JSON file and saves them to a CSV file
# It converts timestamps to US/Eastern time format for better readability.

import json
import csv
from datetime import datetime, timezone
import pytz

def convert_to_eastern(timestamp):
    """Convert UTC timestamp (seconds) to US/Eastern time string."""
    utc_dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    eastern_dt = utc_dt.astimezone(pytz.timezone('US/Eastern'))
    return eastern_dt.strftime('%Y-%m-%d %H:%M:%S')

def extract_comments_to_csv(json_path, csv_path):
    # Optimization: Use streaming JSON parser for large files
    # For very large comment files, consider using ijson library
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    comments = data.get('comments', [])
    columns = [
        'id', 'parent', 'text', 'like_count', 'author', 'author_id', 'author_url',
        'author_is_uploader', 'author_is_verified', 'is_favorited', 'is_pinned',
        'timestamp', '_time_text', 'eastern_time'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        # Optimization: Process comments in batches if needed
        for comment in comments:
            row = {col: comment.get(col, '') for col in columns}
            ts = comment.get('timestamp')
            row['eastern_time'] = convert_to_eastern(ts) if ts else ''
            # Construct author_url if missing
            if not row['author_url'] and row['author_id']:
                row['author_url'] = f"https://www.youtube.com/channel/{row['author_id']}"
            writer.writerow(row)
    
    print(f"CSV file '{csv_path}' created with {len(comments)} comments.")

# To format JSON in VS Code, right-click & select "Format Document" or use Shift+Option+F on macOS.
