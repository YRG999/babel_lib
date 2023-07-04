# bbc news scraper
# original created by:
# https://www.youtube.com/watch?v=zo7yzIVpIJo
# https://github.com/federicoazzu/bbc_headline_scraper/blob/master/main.py

from bs4 import BeautifulSoup
import requests

# Creates a header
headers = {'User-agent': 'Mozilla/5.0'}

# Requests the webpages
request1 = requests.get('https://www.bbc.com/news', headers=headers)
request2 = requests.get('https://www.nytimes.com/', headers=headers)
html1 = request1.content
html2 = request2.content

# Create some soup
soup1 = BeautifulSoup(html1, 'html.parser')
soup2 = BeautifulSoup(html2, 'html.parser')

def bbc_news_scraper():
    news_list = []

    # Finds all the headers in BBC Home
    for h in soup1.findAll('h3', class_='gs-c-promo-heading__title'):
        news_title = h.contents[0].lower()

        if news_title not in news_list:
            if 'bbc' not in news_title:
                news_list.append(news_title)

    # Prints the headers
    print(f'\n--------- BBC ---------')
    for i, title in enumerate(news_list):
        text = ''
        print('BBC', i + 1, ':', title, text)

bbc_news_scraper()

def nyt_news_scraper():
    news_list = []

    # Finds all the headers in New York Times Home
    for h in soup2.findAll('h3'):
        news_title = h.contents[0].lower()

        if news_title not in news_list:
            news_list.append(news_title)

    # Prints the headers
    print(f'\n--------- NYT ---------')
    for i, title in enumerate(news_list):
        text = ''
        print('NYT', i + 1, ':', title, text)

nyt_news_scraper()