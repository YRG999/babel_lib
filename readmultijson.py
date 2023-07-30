# Extract message and username from YouTube Live chat JSON file.

import json
import csv

# filename="text"
filename=input("Enter json file to extract chat\n")

def extract_message_and_author(data):
    actions = data.get('replayChatItemAction', {}).get('actions', [])
    for action in actions:
        item = action.get('addChatItemAction', {}).get('item', {})
        renderer = item.get('liveChatTextMessageRenderer', {})
        message = renderer.get('message', {}).get('runs', [{}])[0].get('text', '')
        author = renderer.get('authorName', {}).get('simpleText', '')
        yield message, author

# Load each JSON object separately
data_list = []
with open(filename, 'r') as json_file:
# with open('MORNING BEEZE [CdDjBVqaEPs].live_chat.json', 'r') as json_file:
    for line in json_file:
        data_list.append(json.loads(line))

# Write to CSV
output_filename = filename+'.csv'
with open(output_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Message', 'AuthorName'])
    for data in data_list:
        for message, author in extract_message_and_author(data):
            writer.writerow([message, author])

print(f"Data written to '{output_filename}'")
