import requests
from bs4 import BeautifulSoup

# Send a request to the webpage
url = 'https://news.google.com/'
response = requests.get(url)

# Parse the webpage using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the data you want to extract
title = soup.title.text
headlines = set()

# Loop over each article and extract its headline
for article in soup.find_all('article'):
    headline = article.find('a', {'aria-label': True})
    if headline:
        headline_text = headline['aria-label']
        if headline_text not in headlines:
            headlines.add(headline_text)
            print(headline_text)

# Write the extracted data to a file
with open('output/website_text.txt', 'a') as file:
    file.write('Title: {}\n'.format(title))
    file.write('Headlines:\n{}\n'.format('\n'.join(headlines)))
    file.write('\n')
