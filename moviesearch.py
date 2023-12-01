import requests
import os
from dotenv import load_dotenv

# Not tested.

# Replace with your actual API key from IMDb
load_dotenv()
api_key = os.getenv("IMDB_API_KEY")

# Define the base URL for the IMDb API
base_url = "https://imdb-api.com/en/API/SearchTitle/"  # This URL might differ - check the IMDb API documentation

# Initialize a dictionary to hold the count of movies per year
movies_per_year = {}

# TODO: Ask for start year and end year of range
# start_year = 2014
# end_year = 2023
# input(#ask for start & end years)
# replace for loop with vars above

# Loop over the past ten years (you need to replace 2014 and 2023 with the actual years you're interested in)
for year in range(2014, 2023 + 1):
    # Construct the full URL for the API request
    url = f"{base_url}{api_key}/{year}"

    # Make the API request
    response = requests.get(url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Parse the JSON result
        data = response.json()

        # Count the number of movies for the year and add to our dictionary
        # This assumes 'data' is a list of movies - you'll need to adapt based on the actual structure of the returned data
        movies_per_year[year] = len(data['results'])
    else:
        print(f"Failed to retrieve data for {year}")

# Print out the results
for year, count in movies_per_year.items():
    print(f"In {year}, {count} movies were released.")
