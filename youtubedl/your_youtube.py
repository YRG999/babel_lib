import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
# CHANNEL_ID = 'CHANNEL_ID_HERE'
MAX_RESULTS = 10

# Build the API request URL
# url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults={MAX_RESULTS}'
url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet,id&order=date&maxResults={MAX_RESULTS}'

# Send the API request and parse the response
response = requests.get(url)
data = json.loads(response.text)

# Append the video titles and URLs to a file
with open('output/recent_videos.txt', 'a') as f:
    for item in data['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        f.write(f"{video_title}: {video_url}\n")
    f.write("\n")
