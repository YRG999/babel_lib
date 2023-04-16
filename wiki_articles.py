import requests
import json
import time

def get_recently_edited_titles():
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'recentchanges',
        'rcprop': 'title',
        'format': 'json',
        'rclimit': '10'
    }
    response = requests.get(url, params=params)
    data = json.loads(response.text)
    titles = [item['title'] for item in data['query']['recentchanges']]
    return titles

filename = 'output/recently_edited_titles.txt'
with open(filename, 'a') as f:
    while True:
        titles = get_recently_edited_titles()
        for title in titles:
            f.write(title + '\n')
        print('Titles written to', filename)
        time.sleep(60)  # wait 1 minute before checking again

# curl "https://en.wikipedia.org/w/api.php?action=query&list=recentchanges&rcprop=title&format=json&rclimit=1"