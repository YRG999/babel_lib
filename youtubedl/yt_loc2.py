import requests
import os
from dotenv import load_dotenv

# combine lat_long & youtube_search_loc

# Load API keys
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
API_KEY_2 = os.getenv("MAPS_API_KEY")

# Enter an address to search
address = input("Enter an address to search:\n")

# Enter a radius in miles
user_radius = input("Enter a radius in miles:\n")
radius = f'{user_radius}mi'

# Convert address to latitude & longitude
url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY_2}'

## Send the API request and parse the response
response = requests.get(url)
data = response.json()

## Extract the latitude and longitude from the response
lat = data['results'][0]['geometry']['location']['lat']
lng = data['results'][0]['geometry']['location']['lng']

## Latitude & longitude for address
location = f'{lat},{lng}'

# Max results
max_results = 10

# Build the YouTube API request URL
url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&part=snippet&location={location}&locationRadius={radius}&type=video&order=date&maxResults={max_results}'

# Send the API request and parse the response
response = requests.get(url)
data = response.json()

# Append the video titles and URLs to a file
with open('output/yt_loc2.txt', 'a') as f:
    for item in data['items']:
        video_title = item['snippet']['title']
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        f.write(f"{video_title}: {video_url}\n")
    f.write('\n')
