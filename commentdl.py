import subprocess
import sys

def download_comments(video_url):
    # Use yt-dlp to download comments from the given video URL
    result = subprocess.run(
        [
            'yt-dlp',
            '--skip-download',
            '--write-comments',
            video_url
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Extract the name of the comments file from the output
    for line in result.stdout.split('\n'):
        if line.strip().startswith('[info] Writing video comments to:'):
            comments_file = line.split(':')[-1].strip()
            return comments_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <youtube_video_url>")
        sys.exit(1)

    video_url = sys.argv[1]
    comments_file = download_comments(video_url)
    
print(f"Comments saved to: {comments_file}")
