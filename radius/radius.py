# radius.py

import googlemaps
import folium
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MAPS_API_KEY2")

# Step 1: Set up Google Maps Client
# api_key = 'YOUR_GOOGLE_MAPS_API_KEY'  # Replace with your API Key
gmaps = googlemaps.Client(key=api_key)

# Step 2: Define the location
location_address = 'Empire State Building, New York, NY'
geocode_result = gmaps.geocode(location_address)
location = geocode_result[0]['geometry']['location']
latitude, longitude = location['lat'], location['lng']

# Step 3: Create a map centered on the location using folium
map_radius = folium.Map(location=[latitude, longitude], zoom_start=13)

# Step 4: Add a circle to the map (e.g., 1 km radius)
radius_meters = 1000  # Radius in meters
folium.Circle(
    location=(latitude, longitude),
    radius=radius_meters,
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.2
).add_to(map_radius)

# Step 5: Save or display the map
map_radius.save("map_with_radius.html")