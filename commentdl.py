# commentdl9.py

import subprocess
import sys
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <youtube_video_url>")
        sys.exit(1)

    video_url = sys.argv[1]
    comments_file = download_comments(video_url)
    
    if comments_file:
        print(f"Comments saved to: {comments_file}")
    else:
        print("Failed to download comments.")

# extract comments
# passes the comments_file name into extractcomments.py 
# to automatically extract the comments 
# into a CSV file with the same name as the JSON file

exec(open("extractcomments.py").read(), {'datetime': datetime, 'pytz': pytz}, {
    'input': lambda prompt: comments_file
})