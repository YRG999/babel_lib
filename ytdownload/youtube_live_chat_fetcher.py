# youtube_live_chat_fetcher10.py
# handle live chat ended

import os
import time
import csv
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from dateutil import parser

# Load environment variables from .env file
load_dotenv()

class LiveChatEnded(Exception):
    """Custom exception to indicate that the live chat has ended."""
    pass

class YouTubeLiveChatFetcher:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.utc = pytz.UTC
        self.eastern = pytz.timezone('US/Eastern')

        # Configure logging for errors and info, excluding extraneous info in the console output
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    def convert_to_eastern(self, timestamp: str) -> str:
        dt = parser.parse(timestamp)
        dt = dt.replace(tzinfo=self.utc)
        eastern_time = dt.astimezone(self.eastern)
        return eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')

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

    def _handle_text_message(self, item: Dict[str, Any]) -> tuple:
        return item['snippet'].get('displayMessage', ''), ''

    def _handle_super_chat(self, item: Dict[str, Any]) -> tuple:
        superchat_details = item['snippet'].get('superChatDetails', {})
        return superchat_details.get('userComment', ''), superchat_details.get('amountDisplayString', '')

    def _handle_super_sticker(self, item: Dict[str, Any]) -> tuple:
        superchat_details = item['snippet'].get('superStickerDetails', {})
        message = f"Super Sticker: {superchat_details.get('superStickerMetadata', {}).get('altText', '')}"
        return message, superchat_details.get('amountDisplayString', '')

    def _handle_new_sponsor(self, item: Dict[str, Any]) -> tuple:
        return "New Sponsor!", ''

    def _handle_other_event(self, item: Dict[str, Any]) -> tuple:
        return f"Other event type: {item['snippet']['type']}", ''

    def fetch_live_chat(self, video_id: str, flush_interval: int = 300) -> None:
        timestamp = datetime.now(self.eastern).strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{video_id}_{timestamp}.csv"
        last_flush_time = time.time()

        try:
            live_chat_id = self._get_live_chat_id(video_id)
            if not live_chat_id:
                return

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp (ET)', 'Author', 'Message', 'Message Type', 'SuperChat Amount'])

                chat_response = self._get_initial_chat_response(live_chat_id)

                while chat_response:
                    try:
                        last_flush_time = self._process_chat_response(
                            chat_response, writer, f, last_flush_time, flush_interval
                        )
                        chat_response = self._get_next_chat_response(chat_response, live_chat_id)
                    except HttpError as e:
                        if e.resp.status in [403, 429]:
                            try:
                                self._handle_http_error(e)
                            except LiveChatEnded:
                                logging.info("Live chat has ended.")
                                break  # Exit the loop gracefully
                            continue  # Retry after handling the error
                        else:
                            logging.error(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
                            break
                    except Exception as e:
                        logging.error(f"An unexpected error occurred: {e}")
                        break
        except KeyboardInterrupt:
            logging.info("Interrupted by user.")
        finally:
            logging.info(f"Chat log saved to {filename}")

    def _get_live_chat_id(self, video_id: str) -> str:
        try:
            video_response = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            ).execute()

            if 'items' not in video_response or not video_response['items']:
                logging.error(f"Video with id {video_id} not found or not a live stream.")
                return ''

            return video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']
        except HttpError as e:
            logging.error(f"An HTTP error {e.resp.status} occurred while fetching live chat ID:\n{e.content}")
            return ''

    def _get_initial_chat_response(self, live_chat_id: str) -> Dict[str, Any]:
        return self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails",
            maxResults=200  # Set maxResults to maximum
        ).execute()

    def _get_next_chat_response(self, chat_response: Dict[str, Any], live_chat_id: str) -> Dict[str, Any]:
        if 'nextPageToken' in chat_response:
            return self.youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet,authorDetails",
                pageToken=chat_response['nextPageToken'],
                maxResults=200  # Set maxResults to maximum
            ).execute()
        return None

    def _process_chat_response(self, chat_response: Dict[str, Any], writer: csv.writer,
                               file_handle, last_flush_time: float, flush_interval: int) -> float:
        for item in chat_response['items']:
            try:
                chat_message = self.get_chat_message(item)
                self._print_chat_message(chat_message)
                writer.writerow([
                    chat_message['timestamp'],
                    chat_message['author'],
                    chat_message['message'],
                    chat_message['type'],
                    chat_message.get('superchat_amount', '')
                ])
            except KeyError as e:
                logging.error(f"Error processing message: {e}")
                continue

        current_time = time.time()
        if current_time - last_flush_time >= flush_interval:
            file_handle.flush()  # Flush the file buffer to disk
            last_flush_time = current_time

        polling_interval = chat_response.get('pollingIntervalMillis', 2000) / 1000  # Default to 2 seconds
        time.sleep(polling_interval)

        return last_flush_time

    def _handle_http_error(self, e: HttpError) -> None:
        error_content = e.content.decode('utf-8') if isinstance(e.content, bytes) else str(e.content)
        error_details = {}
        try:
            error_response = e.error_details[0]
            reason = error_response.get('reason', '')
            message = error_response.get('message', '')
        except (AttributeError, IndexError, KeyError):
            reason = ''
            message = ''

        if reason == 'rateLimitExceeded':
            logging.warning("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        elif reason == 'liveChatEnded':
            logging.info("Encountered 403 Forbidden with reason 'liveChatEnded'.")
            raise LiveChatEnded("The live chat has ended.")
        else:
            logging.error(f"An HTTP error {e.resp.status} occurred:\n{error_content}")
            raise e  # Re-raise the exception for other handlers

    def _print_chat_message(self, chat_message: Dict[str, Any]) -> None:
        if chat_message['type'] == 'superChatEvent':
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['superchat_amount']} - {chat_message['message']}")
        else:
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['message']}")

def main():
    fetcher = YouTubeLiveChatFetcher()
    video_id = input("Enter video ID: ")
    yt_dlp_command = f"yt-dlp --live-from-start -- {video_id}"
    print(f"Run in new terminal to capture live:\n\n\n{yt_dlp_command}\n\n\n")
    input("Press Enter to start capturing live chat...")
    fetcher.fetch_live_chat(video_id)

if __name__ == "__main__":
    main()
