# gnews_scraper3b.py

import requests
from bs4 import BeautifulSoup
import datetime

def fetch_google_news_headlines(limit=5):
    """
    Fetch and display top Google News headlines.
    
    Args:
        limit: Maximum number of headlines to display
    """
    # Optimization: Move request inside function to avoid unnecessary network call on import
    url = 'https://news.google.com/'
    response = requests.get(url)
    
    # Parse the webpage using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    headlines = []
    
    # Loop over each article and extract its headline
    counter = 0
    for article in soup.find_all('article'):
        headline = article.find('h4')
        if headline:
            headline_text = headline.text
            if headline_text not in headlines:
                headlines.append(headline_text)
                counter += 1
                print(f"{counter}. {headline_text}")
                if counter >= limit:
                    break
    
    return headlines

if __name__ == "__main__":
    fetch_google_news_headlines()
    
    # Print the current date and time
    current_datetime = datetime.datetime.now()
    print("\nDate and Time:", current_datetime)
