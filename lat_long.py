import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MAPS_API_KEY")

# Define the location you want to search for
# address = '1600 Amphitheatre Parkway, Mountain View, CA'
print("Enter address (street, city, state):")
address = input()

# Build the API request URL
url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'

# Send the API request and parse the response
response = requests.get(url)
data = response.json()

# Extract the latitude and longitude from the response
lat = data['results'][0]['geometry']['location']['lat']
lng = data['results'][0]['geometry']['location']['lng']

# Print the latitude and longitude
# print(f"Latitude: {lat}")
# print(f"Longitude: {lng}")
print(f"{lat},{lng}")