# gnews_scraper3b.py

import requests
from bs4 import BeautifulSoup
import datetime

# Send a request to the webpage
url = 'https://news.google.com/'
response = requests.get(url)

# Parse the webpage using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the data you want to extract
title = soup.article.div.h4
headlines = []

# Loop over each article and extract its headline
counter = 0  # Counter for limiting the number of headlines
for article in soup.find_all('article'):
    headline = article.find('h4')
    if headline:
        headline_text = headline.text  # Get the text content of the h4 element
        if headline_text not in headlines:
            headlines.append(headline_text)
            counter += 1
            print(f"{counter}. {headline_text}")
            if counter >= 5:  # Limit the number of headlines to display (e.g., top 5)
                break

# Print the current date and time
current_datetime = datetime.datetime.now()
print("\nDate and Time:", current_datetime)
