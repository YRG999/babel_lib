import requests
import json
import time
from datetime import datetime

def get_time():
    now = datetime.now() # https://www.w3resource.com/python-exercises/python-basic-exercise-3.php
    date_time = now.strftime("%Y%m%d %H_%M_%S")
    return date_time

def get_recently_edited_titles():
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'recentchanges', # https://en.wikipedia.org/w/api.php?action=help&modules=query%2Brecentchanges
        'rcprop': 'title',
        'format': 'json',
        'rclimit': '10'
    }
    response = requests.get(url, params=params)
    data = json.loads(response.text)
    titles = [item['title'] for item in data['query']['recentchanges']]
    return titles

filename = 'output/recently_edited_titles.txt'
while True:
    current_date_time = get_time()
    titles = get_recently_edited_titles()
    
    # Fix: Open file inside loop to avoid handle leak
    with open(filename, 'a') as f:
        f.write('\n' + current_date_time + '\n\n')
        for title in titles:
            f.write(title + '\n')
    
    print('Titles written to', filename)
    time.sleep(60)  # wait 1 minute before checking again

# curl "https://en.wikipedia.org/w/api.php?action=query&list=recentchanges&rcprop=title&format=json&rclimit=1"