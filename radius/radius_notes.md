# radius notes

To create a tool that draws a radius around a location on a map using the Google Maps API and Python, you’ll primarily work with the Google Maps JavaScript API for visualizing the map and the `gmplot` library or `folium` for easy plotting in Python. Here’s a step-by-step guide to accomplish this:

## Step 1: Set up Google Maps API Key

1. Get an API Key from [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Maps JavaScript API** and **Geocoding API**.

## Step 2: Install Necessary Libraries

Install libraries that will help you interact with the Google Maps API and plot maps.

```bash
pip install googlemaps folium
```

## Step 3: Geocode a Location and Calculate Points

1. Use the Google Maps API to geocode an address or location to get its latitude and longitude.
2. Use `folium` in Python to create a map and draw a circle with a specified radius around the location.

## Step 4: Implement the Tool in Python

Here’s a Python script to create a radius tool around a specific location:

```python
import googlemaps
import folium

# Step 1: Set up Google Maps Client
api_key = 'YOUR_GOOGLE_MAPS_API_KEY'  # Replace with your API Key
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
```

## Step 5: Viewing the Map

Running this script will create an HTML file called `map_with_radius.html`. Open it in your browser to view the map with the drawn radius.

## Explanation of Key Components

1. **Google Maps API**: Used for geocoding the location.
2. **Folium**: Helps create an interactive map and draw a circle with the specified radius around the geocoded location.
3. **`radius_meters`**: Adjust the radius as needed in meters to define the circle size.

This is a lightweight, interactive solution with Python for visualizing a radius around a location, using folium for easy mapping and Google Maps API for accurate location data. Let me know if you’d like to expand this, maybe by adding multiple locations or custom styling!

---

The `REQUEST_DENIED` error indicates that billing isn’t enabled for your Google Cloud project, which is required for accessing Google Maps API services.

## Here’s how you can enable billing:

1. **Go to Google Cloud Console**:
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/).

2. **Enable Billing**:
   - Select your project (the one you're using for the Google Maps API).
   - Go to the **Billing** section. If it’s not set up, you’ll be prompted to add a billing account.
   - Add your payment information and link the billing account to your project.

3. **Verify API Access**:
   - Make sure the **Maps JavaScript API** and **Geocoding API** are enabled.
   - Double-check the **API Key** permissions under **APIs & Services > Credentials** and ensure that your key is unrestricted for testing (or restricted correctly for security if used in production).

After enabling billing and verifying that the APIs are enabled, retry running the script. Google offers a free tier for Maps API usage, so you might not incur charges for small, limited use cases like testing.

---

## links

- <https://console.cloud.google.com/home/dashboard>
