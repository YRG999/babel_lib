# youtube-live-chat-fetcher4.py
# run pip install google-api-python-client
# handle rate limiting
# save to csv

import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('YOUTUBE_API_KEY')

def save_chat_to_file(chat_messages, video_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_log_{video_id}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Author', 'Message'])  # Write header
        for message in chat_messages:
            writer.writerow([message['timestamp'], message['author'], message['message']])
    
    print(f"Chat log saved to {filename}")

def main():
    youtube = build('youtube', 'v3', developerKey=api_key)

    # To save live video
    # In one window, run: yt-dlp --live-from-start VIDEO_ID
    # In another window, run: python youtube-live-chat-fetcher.py

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
                message = item['snippet']['displayMessage']
                author = item['authorDetails']['displayName']
                timestamp = item['snippet']['publishedAt']
                
                chat_message = {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message
                }
                chat_messages.append(chat_message)
                
                print(f"{timestamp} - {author}: {message}")

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