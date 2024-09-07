# youtube-live-chat-fetcher6.py
# run pip install google-api-python-client
# handle rate limiting
# save to csv
# Add types of chat events: super chats, member join notifactions, andother special events
# convert time to EST
# Display superchat message & amount

import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from dateutil import parser

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('YOUTUBE_API_KEY')

# Set up time zones
utc = pytz.UTC
eastern = pytz.timezone('US/Eastern')

def convert_to_eastern(timestamp):
    dt = parser.parse(timestamp)
    dt = dt.replace(tzinfo=utc)
    eastern_time = dt.astimezone(eastern)
    return eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def save_chat_to_file(chat_messages, video_id):
    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    filename = f"chat_log_{video_id}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp (ET)', 'Author', 'Message', 'Message Type', 'SuperChat Amount'])  # Updated header
        for message in chat_messages:
            writer.writerow([
                message['timestamp'],
                message['author'],
                message['message'],
                message['type'],
                message.get('superchat_amount', '')  # Add SuperChat amount
            ])
    
    print(f"Chat log saved to {filename}")

def get_chat_message(item):
    message_type = item['snippet']['type']
    author = item['authorDetails']['displayName']
    timestamp = convert_to_eastern(item['snippet']['publishedAt'])
    
    if message_type == 'textMessageEvent':
        message = item['snippet'].get('displayMessage', '')
        superchat_amount = ''
    elif message_type == 'superChatEvent':
        superchat_details = item['snippet'].get('superChatDetails', {})
        amount = superchat_details.get('amountDisplayString', '')
        message = superchat_details.get('userComment', '')
        superchat_amount = amount
    elif message_type == 'superStickerEvent':
        superchat_details = item['snippet'].get('superStickerDetails', {})
        amount = superchat_details.get('amountDisplayString', '')
        message = f"Super Sticker: {superchat_details.get('superStickerMetadata', {}).get('altText', '')}"
        superchat_amount = amount
    elif message_type == 'newSponsorEvent':
        message = "New Sponsor!"
        superchat_amount = ''
    else:
        message = f"Other event type: {message_type}"
        superchat_amount = ''
    
    return {
        'timestamp': timestamp,
        'author': author,
        'message': message,
        'type': message_type,
        'superchat_amount': superchat_amount
    }

def main():
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_id = input("Enter video ID: ")
    save_interval = 300  # Save every 5 minutes (300 seconds)
    last_save_time = time.time()
    chat_messages = []

    try:
        # Get live chat id
        video_response = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        ).execute()

        if 'items' not in video_response or not video_response['items']:
            print(f"Video with id {video_id} not found or not a live stream.")
            return

        live_chat_id = video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']

        # Get live chat messages
        chat_response = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails"
        ).execute()

        while chat_response:
            for item in chat_response['items']:
                try:
                    chat_message = get_chat_message(item)
                    chat_messages.append(chat_message)
                    if chat_message['type'] == 'superChatEvent':
                        print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['superchat_amount']} - {chat_message['message']}")
                    else:
                        print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['message']}")
                except KeyError as e:
                    print(f"Error processing message: {e}")
                    continue

            # Check if it's time to save the chat log
            current_time = time.time()
            if current_time - last_save_time >= save_interval:
                save_chat_to_file(chat_messages, video_id)
                last_save_time = current_time
                chat_messages = []  # Clear the list after saving

            # Wait for the polling interval before making the next request
            polling_interval = chat_response['pollingIntervalMillis'] / 1000
            time.sleep(polling_interval)

            if 'nextPageToken' in chat_response:
                chat_response = youtube.liveChatMessages().list(
                    liveChatId=live_chat_id,
                    part="snippet,authorDetails",
                    pageToken=chat_response['nextPageToken']
                ).execute()
            else:
                chat_response = None

    except HttpError as e:
        error_details = e.error_details[0]
        if error_details['reason'] == 'rateLimitExceeded':
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        else:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")

    finally:
        # Save any remaining chat messages before exiting
        if chat_messages:
            save_chat_to_file(chat_messages, video_id)

if __name__ == "__main__":
    main()