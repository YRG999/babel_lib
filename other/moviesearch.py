# moviesearch2.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("IMDB_API_KEY")
base_url = "https://imdb-api.com/en/API/SearchTitle/" # https://aws.amazon.com/marketplace/pp/prodview-3n67c76ppu2yy#overview
movies_per_year = {}
for year in range(2014, 2023 + 1):
    url = f"{base_url}{api_key}/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        movies_per_year[year] = len(data['results'])
    else:
        print(f"Failed to retrieve data for {year}")

for year, count in movies_per_year.items():
    print(f"In {year}, {count} movies were released.")