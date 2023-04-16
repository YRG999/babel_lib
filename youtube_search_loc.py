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

# New york l/l
# 40.7128° N, 74.0060° W
# 40.712800, -74.006000
# Coachella - Empire Polo Field, Indio, CA
# 33.6801481,-116.239591

# Build the API request URL
# url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&location={location}&type=video&order=date&maxResults={max_results}'
# url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&type=video&order=date&maxResults={max_results}'
url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&location={location}&locationRadius={radius}&type=video&order=date&maxResults={max_results}'

# Send the API request and parse the response
response = requests.get(url)
data = response.json()

# Print API key
# print(f"{API_KEY}")

# # Print response
# print(f"{data}")

# # Print the video titles and URLs to console
# for item in data['items']:
#     video_title = item['snippet']['title']
#     video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
#     print(f"{video_title}: {video_url}")

# Print to file not console:

# import requests

# # Define the search parameters
# location = 'New York'
# max_results = 10

# # Build the API request URL
# url = f'https://www.googleapis.com/youtube/v3/search?key=YOUR_API_KEY_HERE&part=snippet&location={location}&type=video&order=date&maxResults={max_results}'

# # Send the API request and parse the response
# response = requests.get(url)
# data = response.json()

# Append the video titles and URLs to a file
with open('youtube_search_loc.txt', 'a') as f:
    for item in data['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        f.write(f"{video_title}: {video_url}\n")
