# youtube_live_chat_fetcher7.py
# handle rate limiting
# save to csv
# Add types of chat events: super chats, member join notifactions, andother special events
# convert time to EST
# display superchat message & amount
# optimize code using classes
# add instructions to download live video

import os
import time
import csv
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from dateutil import parser

# Load environment variables from .env file
load_dotenv()

class YouTubeLiveChatFetcher:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.utc = pytz.UTC
        self.eastern = pytz.timezone('US/Eastern')

    def convert_to_eastern(self, timestamp: str) -> str:
        dt = parser.parse(timestamp)
        dt = dt.replace(tzinfo=self.utc)
        eastern_time = dt.astimezone(self.eastern)
        return eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    def save_chat_to_file(self, chat_messages: List[Dict[str, Any]], video_id: str) -> None:
        timestamp = datetime.now(self.eastern).strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{video_id}_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp (ET)', 'Author', 'Message', 'Message Type', 'SuperChat Amount'])
            for message in chat_messages:
                writer.writerow([
                    message['timestamp'],
                    message['author'],
                    message['message'],
                    message['type'],
                    message.get('superchat_amount', '')
                ])
        
        print(f"Chat log saved to {filename}")

    def get_chat_message(self, item: Dict[str, Any]) -> Dict[str, Any]:
        message_type = item['snippet']['type']
        author = item['authorDetails']['displayName']
        timestamp = self.convert_to_eastern(item['snippet']['publishedAt'])
        
        message_handlers = {
            'textMessageEvent': self._handle_text_message,
            'superChatEvent': self._handle_super_chat,
            'superStickerEvent': self._handle_super_sticker,
            'newSponsorEvent': self._handle_new_sponsor
        }
        
        handler = message_handlers.get(message_type, self._handle_other_event)
        message, superchat_amount = handler(item)
        
        return {
            'timestamp': timestamp,
            'author': author,
            'message': message,
            'type': message_type,
            'superchat_amount': superchat_amount
        }

    def _handle_text_message(self, item: Dict[str, Any]) -> tuple[str, str]:
        return item['snippet'].get('displayMessage', ''), ''

    def _handle_super_chat(self, item: Dict[str, Any]) -> tuple[str, str]:
        superchat_details = item['snippet'].get('superChatDetails', {})
        return superchat_details.get('userComment', ''), superchat_details.get('amountDisplayString', '')

    def _handle_super_sticker(self, item: Dict[str, Any]) -> tuple[str, str]:
        superchat_details = item['snippet'].get('superStickerDetails', {})
        message = f"Super Sticker: {superchat_details.get('superStickerMetadata', {}).get('altText', '')}"
        return message, superchat_details.get('amountDisplayString', '')

    def _handle_new_sponsor(self, item: Dict[str, Any]) -> tuple[str, str]:
        return "New Sponsor!", ''

    def _handle_other_event(self, item: Dict[str, Any]) -> tuple[str, str]:
        return f"Other event type: {item['snippet']['type']}", ''

    def fetch_live_chat(self, video_id: str, save_interval: int = 300) -> None: # Save every 5 minutes (300 seconds)
        last_save_time = time.time()
        chat_messages = []

        try:
            live_chat_id = self._get_live_chat_id(video_id)
            if not live_chat_id:
                return

            chat_response = self._get_initial_chat_response(live_chat_id)

            while chat_response:
                chat_messages, last_save_time = self._process_chat_response(
                    chat_response, chat_messages, last_save_time, save_interval, video_id
                )

                chat_response = self._get_next_chat_response(chat_response, live_chat_id)

        except HttpError as e:
            self._handle_http_error(e)

        finally:
            if chat_messages:
                self.save_chat_to_file(chat_messages, video_id)

    def _get_live_chat_id(self, video_id: str) -> str:
        video_response = self.youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        ).execute()

        if 'items' not in video_response or not video_response['items']:
            print(f"Video with id {video_id} not found or not a live stream.")
            return ''

        return video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']

    def _get_initial_chat_response(self, live_chat_id: str) -> Dict[str, Any]:
        return self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails"
        ).execute()

    def _process_chat_response(self, chat_response: Dict[str, Any], chat_messages: List[Dict[str, Any]],
                               last_save_time: float, save_interval: int, video_id: str) -> tuple[List[Dict[str, Any]], float]:
        for item in chat_response['items']:
            try:
                chat_message = self.get_chat_message(item)
                chat_messages.append(chat_message)
                self._print_chat_message(chat_message)
            except KeyError as e:
                print(f"Error processing message: {e}")
                continue

        current_time = time.time()
        if current_time - last_save_time >= save_interval:
            self.save_chat_to_file(chat_messages, video_id)
            last_save_time = current_time
            chat_messages = []

        polling_interval = chat_response['pollingIntervalMillis'] / 1000
        time.sleep(polling_interval)

        return chat_messages, last_save_time

    def _get_next_chat_response(self, chat_response: Dict[str, Any], live_chat_id: str) -> Dict[str, Any]:
        if 'nextPageToken' in chat_response:
            return self.youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails",
                pageToken=chat_response['nextPageToken']
            ).execute()
        return None

    def _handle_http_error(self, e: HttpError) -> None:
        error_details = e.error_details[0]
        if error_details['reason'] == 'rateLimitExceeded':
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        else:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")

    def _print_chat_message(self, chat_message: Dict[str, Any]) -> None:
        if chat_message['type'] == 'superChatEvent':
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['superchat_amount']} - {chat_message['message']}")
        else:
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['message']}")

def main():
    fetcher = YouTubeLiveChatFetcher()
    video_id = input("Enter video ID: ")
    yt_dlp_command = f"yt-dlp --live-from-start -- {video_id}"
    print (f"Run in new terminal to capture live:\n\n\n{yt_dlp_command}\n\n\n")
    input("Press Enter to start capturing live chat...")
    fetcher.fetch_live_chat(video_id)

if __name__ == "__main__":
    main()