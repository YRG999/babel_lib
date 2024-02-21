import requests
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Define the search parameters
location = '33.6801481,-116.239591'
radius = '1mi'
max_results = 10

url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&location={location}&locationRadius={radius}&type=video&order=date&maxResults={max_results}'

# Send the API request and parse the response
response = requests.get(url)
data = response.json()

# Append the video titles and URLs to a file
with open('youtube_search_loc.txt', 'a') as f:
    for item in data['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        f.write(f"{video_title}: {video_url}\n")
