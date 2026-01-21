# livechat.py
#   - See livechat_README.md for usage instructions and version history.

import os
import sys
import time
import csv
import logging
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable, Optional, Tuple
from contextlib import contextmanager
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

class QuotaExceeded(Exception):
    """Custom exception to indicate that the API quota has been exceeded."""
    pass

class UnrecoverableAPIError(Exception):
    """Custom exception for unrecoverable API errors."""
    pass


class QuotaManager:
    """Share daily YouTube API quota usage across multiple processes."""

    def __init__(
        self,
        max_daily_quota: int = 10000,
        storage_path: Optional[Path] = None,
        timezone: Optional[pytz.BaseTzInfo] = None,
    ) -> None:
        self.max_daily_quota = max_daily_quota
        self.storage_path = Path(storage_path) if storage_path else Path(__file__).resolve().with_name('.youtube_quota.json')
        self.timezone = timezone or pytz.UTC
        try:
            import fcntl  # type: ignore

            self._lock_module = fcntl
        except ImportError:
            self._lock_module = None

    @contextmanager
    def _locked_file(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        mode = 'r+' if self.storage_path.exists() else 'w+'
        with open(self.storage_path, mode) as file_handle:
            if self._lock_module:
                self._lock_module.flock(file_handle.fileno(), self._lock_module.LOCK_EX)
            try:
                yield file_handle
            finally:
                if self._lock_module:
                    self._lock_module.flock(file_handle.fileno(), self._lock_module.LOCK_UN)

    def _today_key(self) -> str:
        return datetime.now(self.timezone).strftime('%Y-%m-%d')

    def _default_state(self) -> Dict[str, Any]:
        return {
            'date': self._today_key(),
            'used': 0,
            'entries': [],
        }

    def _read_state(self, file_handle) -> Tuple[Dict[str, Any], bool]:
        file_handle.seek(0)
        raw = file_handle.read()
        dirty = False
        if raw:
            try:
                state = json.loads(raw)
            except json.JSONDecodeError:
                state = self._default_state()
                dirty = True
        else:
            state = self._default_state()
            dirty = True

        if state.get('date') != self._today_key():
            state = self._default_state()
            dirty = True

        if 'used' not in state:
            state['used'] = 0
            dirty = True

        if 'entries' not in state:
            state['entries'] = []
            dirty = True

        return state, dirty

    def _write_state(self, file_handle, state: Dict[str, Any]) -> None:
        file_handle.seek(0)
        file_handle.truncate()
        json.dump(state, file_handle)
        file_handle.flush()
        try:
            os.fsync(file_handle.fileno())
        except OSError:
            pass

    def remaining_quota(self) -> int:
        with self._locked_file() as file_handle:
            state, dirty = self._read_state(file_handle)
            remaining = max(self.max_daily_quota - state['used'], 0)
            if dirty:
                self._write_state(file_handle, state)
            return remaining

    def log_consumption(self, cost: int, note: str = '') -> int:
        with self._locked_file() as file_handle:
            state, _ = self._read_state(file_handle)

            if cost > 0:
                state['used'] = min(self.max_daily_quota, state['used'] + cost)

            state['entries'].append({
                'timestamp': datetime.now(self.timezone).isoformat(),
                'cost': cost,
                'note': note,
            })
            state['entries'] = state['entries'][-100:]

            self._write_state(file_handle, state)
            return state['used']

    def register_session(self, video_id: str, expected_duration_seconds: float) -> None:
        hours = expected_duration_seconds / 3600.0
        note = f'Start session video={video_id} expected_hours={hours:.2f}'
        self.log_consumption(0, note)

class YouTubeLiveChatFetcher:
    def __init__(self, expected_duration_hours: float = 4.0, quota_manager: Optional[QuotaManager] = None):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.utc = pytz.UTC
        self.eastern = pytz.timezone('US/Eastern')

        # Configure logging for errors and info, excluding extraneous info in the console output
        logging.basicConfig(level=logging.INFO, format='%(message)s')

        # Quota management
        self.MAX_DAILY_QUOTA = 10000
        self.LIVE_CHAT_MESSAGES_COST = 5
        self.VIDEOS_LIST_COST = 1  # Cost for videos.list API call
        self.quota_manager = quota_manager or QuotaManager(
            max_daily_quota=self.MAX_DAILY_QUOTA,
            timezone=self.eastern,
        )

        # Expected live stream duration in seconds
        self.expected_duration = expected_duration_hours * 3600  # Convert hours to seconds

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
        termination_reason = None  # Variable to hold termination reason
        start_time = time.time()

        self.quota_manager.register_session(video_id, self.expected_duration)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp (ET)', 'Author', 'Message', 'Message Type', 'SuperChat Amount'])

            try:
                live_chat_id = self._get_live_chat_id(video_id)
                if not live_chat_id:
                    termination_reason = "Live chat ID not found."
                    return

                remaining_quota = self.quota_manager.remaining_quota()
                if remaining_quota < self.LIVE_CHAT_MESSAGES_COST:
                    termination_reason = "No quota available for live chat messages."
                    logging.info(termination_reason)
                    return

                chat_response = self._get_initial_chat_response(live_chat_id)

                while chat_response:
                    remaining_quota = self.quota_manager.remaining_quota()
                    polling_interval = self._calculate_polling_interval(chat_response, start_time, remaining_quota)
                    try:
                        last_flush_time = self._process_chat_response(
                            chat_response, writer, f, last_flush_time, flush_interval
                        )

                        if remaining_quota < self.LIVE_CHAT_MESSAGES_COST:
                            termination_reason = "Quota exhausted before next poll."
                            logging.info(termination_reason)
                            break

                        chat_response = self._get_next_chat_response(chat_response, live_chat_id)

                    except HttpError as e:
                        try:
                            self._handle_http_error(e)
                        except (LiveChatEnded, QuotaExceeded, UnrecoverableAPIError) as ex:
                            logging.info(str(ex))
                            termination_reason = str(ex)
                            break  # Exit the loop gracefully
                        time.sleep(polling_interval)
                        continue  # Retry after handling the error
                    except QuotaExceeded as ex:
                        logging.info(str(ex))
                        termination_reason = str(ex)
                        break
                    except Exception as e:
                        logging.error(f"An unexpected error occurred: {e}")
                        termination_reason = f"An unexpected error occurred: {e}"
                        break

                    if chat_response:
                        time.sleep(polling_interval)

            except KeyboardInterrupt:
                logging.info("Interrupted by user.")
                termination_reason = "Interrupted by user."
            except QuotaExceeded as ex:
                logging.info(str(ex))
                termination_reason = str(ex)
            except HttpError as e:
                try:
                    self._handle_http_error(e)
                except (LiveChatEnded, QuotaExceeded, UnrecoverableAPIError) as ex:
                    logging.info(str(ex))
                    termination_reason = str(ex)
                else:
                    termination_reason = f"HTTP error during setup: {e}"
            finally:
                if termination_reason:
                    writer.writerow(['Termination Reason:', termination_reason])
                    f.flush()  # Ensure it's written to disk
                logging.info(f"Chat log saved to {filename}")

    def _get_live_chat_id(self, video_id: str) -> str:
        request = self.youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )

        try:
            video_response = self._execute_quota_guarded_request(
                self.VIDEOS_LIST_COST,
                f"videos.list video={video_id}",
                request.execute
            )
        except HttpError as e:
            logging.error(f"An HTTP error {e.resp.status} occurred while fetching live chat ID:\n{e.content}")
            return ''

        if 'items' not in video_response or not video_response['items']:
            logging.error(f"Video with id {video_id} not found or not a live stream.")
            return ''

        return video_response['items'][0]['liveStreamingDetails']['activeLiveChatId']

    def _get_initial_chat_response(self, live_chat_id: str) -> Dict[str, Any]:
        request = self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails",
            maxResults=200  # Set maxResults to maximum
        )

        return self._execute_quota_guarded_request(
            self.LIVE_CHAT_MESSAGES_COST,
            f"liveChatMessages.list initial live_chat_id={live_chat_id}",
            request.execute
        )

    def _get_next_chat_response(self, chat_response: Dict[str, Any], live_chat_id: str) -> Optional[Dict[str, Any]]:
        if 'nextPageToken' not in chat_response:
            return None

        request = self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet,authorDetails",
            pageToken=chat_response['nextPageToken'],
            maxResults=200  # Set maxResults to maximum
        )

        return self._execute_quota_guarded_request(
            self.LIVE_CHAT_MESSAGES_COST,
            f"liveChatMessages.list page live_chat_id={live_chat_id}",
            request.execute
        )

    def _execute_quota_guarded_request(
        self,
        cost: int,
        note: str,
        request_callable: Callable[[], Dict[str, Any]]
    ) -> Dict[str, Any]:
        remaining = self.quota_manager.remaining_quota()
        if remaining < cost:
            raise QuotaExceeded(
                f"Quota exhausted: needed {cost} units for {note}, remaining={remaining}."
            )

        response = request_callable()
        self.quota_manager.log_consumption(cost, note)
        return response

    def _calculate_polling_interval(
        self,
        chat_response: Dict[str, Any],
        start_time: float,
        remaining_quota: int
    ) -> float:
        interval_hint_ms = chat_response.get('pollingIntervalMillis', 5000)
        interval_hint = max(interval_hint_ms / 1000.0, 5.0)

        elapsed = max(time.time() - start_time, 0.0)
        remaining_time = max(self.expected_duration - elapsed, 5.0)
        remaining_calls = max(remaining_quota // self.LIVE_CHAT_MESSAGES_COST, 1)

        budget_interval = remaining_time / remaining_calls if remaining_calls else remaining_time
        return max(interval_hint, budget_interval, 5.0)

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

        return last_flush_time

    def _handle_http_error(self, e: HttpError) -> None:
        error_content = e.content.decode('utf-8') if isinstance(e.content, bytes) else str(e.content)
        try:
            error_response = e.error_details[0]
            if isinstance(error_response, dict):
                reason = error_response.get('reason', '')
                message = error_response.get('message', '')
            else:
                reason = ''
                message = str(error_response)
        except (AttributeError, IndexError, KeyError):
            reason = ''
            message = ''

        if reason == 'rateLimitExceeded':
            logging.warning("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        elif reason == 'liveChatEnded':
            logging.info("Live chat has ended.")
            raise LiveChatEnded("Live chat has ended.")
        elif reason == 'quotaExceeded':
            logging.error("API quota has been exceeded.")
            raise QuotaExceeded("API quota has been exceeded.")
        else:
            # For any other error, log the reason and message
            logging.error(f"An HTTP error occurred: {reason} - {message}")
            print(f"An HTTP error occurred: {reason} - {message}")
            raise UnrecoverableAPIError(f"An HTTP error occurred: {reason} - {message}")

    def _print_chat_message(self, chat_message: Dict[str, Any]) -> None:
        if chat_message['type'] == 'superChatEvent':
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['superchat_amount']} - {chat_message['message']}")
        else:
            print(f"{chat_message['timestamp']} - {chat_message['author']} ({chat_message['type']}): {chat_message['message']}")

def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    # If it doesn't contain common URL patterns, assume it's already a video ID
    if not any(pattern in url_or_id for pattern in ['youtube.com', 'youtu.be']):
        return url_or_id

    # Common YouTube URL patterns
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',  # Embed URLs
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',  # Watch URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # If no pattern matches, return original (might be an ID already)
    return url_or_id

def get_venv_activation_command() -> Optional[str]:
    """Detect if running in a virtual environment and return the activation command."""
    # Check if we're in a virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')

    if not venv_path:
        # Alternative check: compare sys.prefix with sys.base_prefix
        if hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix:
            venv_path = sys.prefix
        else:
            return None

    # Build activation command based on platform
    import platform
    system = platform.system()

    if system == 'Windows':
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    else:  # Unix-like (macOS, Linux)
        activate_script = os.path.join(venv_path, 'bin', 'activate')

    if os.path.exists(activate_script):
        return activate_script

    return None

def open_terminal_with_ytdlp(video_id: str) -> None:
    """Open a new terminal window and start downloading the live stream with yt-dlp."""
    base_command = f"yt-dlp --live-from-start -- {video_id}"

    # Get virtual environment activation command if applicable
    venv_activate = get_venv_activation_command()

    # Detect platform
    import platform
    system = platform.system()

    if system == 'Darwin':  # macOS
        # Build the full command with venv activation
        if venv_activate:
            full_command = f'source "{venv_activate}" && {base_command}'
            logging.info(f"Activating virtual environment: {venv_activate}")
        else:
            full_command = base_command

        # Use osascript to open a new Terminal window
        # Need to escape quotes for AppleScript
        escaped_command = full_command.replace('"', '\\"')
        script = f'''
        tell application "Terminal"
            do script "{escaped_command}"
            activate
        end tell
        '''
        subprocess.Popen(['osascript', '-e', script])
        logging.info(f"Opened new terminal window with command: {full_command}")

    elif system == 'Linux':
        # Build the full command with venv activation
        if venv_activate:
            full_command = f'source "{venv_activate}" && {base_command}; exec bash'
        else:
            full_command = f'{base_command}; exec bash'

        # Try common Linux terminal emulators
        terminals = ['gnome-terminal', 'konsole', 'xterm']
        for term in terminals:
            try:
                if term == 'gnome-terminal':
                    subprocess.Popen([term, '--', 'bash', '-c', full_command])
                elif term == 'konsole':
                    subprocess.Popen([term, '-e', 'bash', '-c', full_command])
                else:
                    subprocess.Popen([term, '-e', 'bash', '-c', full_command])
                logging.info(f"Opened new terminal window ({term}) with command: {full_command}")
                break
            except FileNotFoundError:
                continue

    elif system == 'Windows':
        # Build the full command with venv activation
        if venv_activate:
            full_command = f'"{venv_activate}" && {base_command}'
        else:
            full_command = base_command

        subprocess.Popen(['start', 'cmd', '/k', full_command], shell=True)
        logging.info(f"Opened new command prompt with command: {full_command}")
    else:
        logging.warning(f"Unsupported platform: {system}. Please run manually: {base_command}")

def main():
    expected_duration_hours = float(input("Enter expected live stream duration in hours (e.g., 4): "))
    fetcher = YouTubeLiveChatFetcher(expected_duration_hours=expected_duration_hours)

    # Accept full YouTube URL or video ID
    url_input = input("Enter YouTube URL or video ID: ")
    video_id = extract_video_id(url_input)

    print(f"\nExtracted video ID: {video_id}")

    # Toggle for downloading video or just capturing chat
    download_video = input("Download video as well? (y/n) [y]: ").strip().lower()
    if download_video != 'n':
        print(f"Opening new terminal window to download live stream...")
        open_terminal_with_ytdlp(video_id)
        time.sleep(2)  # Give terminal time to open

    print(f"\nStarting live chat capture...")

    # Start capturing chat
    fetcher.fetch_live_chat(video_id)

if __name__ == "__main__":
    main()
