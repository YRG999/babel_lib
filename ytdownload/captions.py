# livecaptions.py
#   - Capture live transcriptions from YouTube live streams using yt-dlp + Whisper
#   - Similar interface to livechat.py
#   - Uses mlx-whisper (optimized for Apple Silicon)

import os
import sys
import time
import csv
import logging
import re
import subprocess
import tempfile
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


def check_dependencies() -> dict:
    """Check for required dependencies and return status."""
    status = {
        'yt-dlp': False,
        'ffmpeg': False,
        'mlx-whisper': False,
    }

    # Check yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        status['yt-dlp'] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        status['ffmpeg'] = result.returncode == 0
    except FileNotFoundError:
        pass

    # Check mlx-whisper
    try:
        import mlx_whisper
        status['mlx-whisper'] = True
    except ImportError:
        pass

    return status


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    if not any(pattern in url_or_id for pattern in ['youtube.com', 'youtu.be']):
        return url_or_id

    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return url_or_id


class LiveCaptionFetcher:
    """Fetch and transcribe live captions from YouTube streams."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
        chunk_duration: int = 10,
    ):
        """
        Initialize the caption fetcher.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large, large-v3)
            language: Language code for transcription
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.model_size = model_size
        self.language = language
        self.chunk_duration = chunk_duration
        self.eastern = pytz.timezone('US/Eastern')
        self._stop_event = threading.Event()

        # Map model sizes to mlx-whisper model names
        self.model_map = {
            'tiny': 'mlx-community/whisper-tiny',
            'base': 'mlx-community/whisper-base',
            'small': 'mlx-community/whisper-small',
            'medium': 'mlx-community/whisper-medium',
            'large': 'mlx-community/whisper-large-v3',
            'large-v3': 'mlx-community/whisper-large-v3',
        }

    def _get_stream_url(self, video_id: str) -> Optional[str]:
        """Get the audio stream URL for a YouTube video."""
        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            result = subprocess.run(
                [
                    'yt-dlp',
                    '-f', 'bestaudio',
                    '-g',  # Get URL only
                    '--no-warnings',
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                logging.error(f"yt-dlp error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logging.error("Timeout getting stream URL")
            return None
        except Exception as e:
            logging.error(f"Error getting stream URL: {e}")
            return None

    def _stream_audio_chunks(
        self,
        video_id: str,
        temp_dir: str,
        audio_queue: queue.Queue,
    ) -> None:
        """
        Stream audio from YouTube and save chunks to temp directory.
        Runs in a separate thread.
        """
        chunk_index = 0
        stream_url = self._get_stream_url(video_id)

        if not stream_url:
            audio_queue.put(None)
            return

        logging.info("Starting audio capture...")
        start_time = datetime.now(self.eastern)
        url = f"https://www.youtube.com/watch?v={video_id}"
        consecutive_failures = 0
        max_failures = 5

        while not self._stop_event.is_set():
            chunk_file = os.path.join(temp_dir, f"chunk_{chunk_index:05d}.wav")
            chunk_start_time = start_time + timedelta(seconds=chunk_index * self.chunk_duration)

            try:
                # Capture a chunk of audio
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite
                    '-i', stream_url,
                    '-t', str(self.chunk_duration),
                    '-vn',  # No video
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',  # 16kHz for Whisper
                    '-ac', '1',  # Mono
                    '-loglevel', 'error',
                    chunk_file,
                ]

                process = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.chunk_duration + 30,
                )

                if process.returncode == 0 and os.path.exists(chunk_file):
                    file_size = os.path.getsize(chunk_file)
                    if file_size > 1000:  # Minimum valid file size
                        audio_queue.put((chunk_file, chunk_start_time))
                        chunk_index += 1
                        consecutive_failures = 0
                    else:
                        logging.warning(f"Chunk too small ({file_size} bytes), skipping")
                        try:
                            os.remove(chunk_file)
                        except OSError:
                            pass
                        consecutive_failures += 1
                else:
                    consecutive_failures += 1
                    if process.stderr:
                        stderr_lower = process.stderr.lower()
                        # Check if stream ended or URL expired
                        if '403' in process.stderr or 'forbidden' in stderr_lower:
                            logging.info("Stream URL expired, refreshing...")
                            new_url = self._get_stream_url(video_id)
                            if new_url:
                                stream_url = new_url
                                logging.info("Got new stream URL")
                                consecutive_failures = 0
                                continue
                        elif 'end of file' in stderr_lower or 'eof' in stderr_lower:
                            logging.info("Stream appears to have ended")
                            break

                if consecutive_failures >= max_failures:
                    logging.error(f"Too many consecutive failures ({max_failures}), stopping")
                    break

            except subprocess.TimeoutExpired:
                logging.warning("Audio capture timeout, continuing...")
                consecutive_failures += 1
                continue
            except Exception as e:
                logging.error(f"Error capturing audio: {e}")
                consecutive_failures += 1
                time.sleep(1)
                continue

        # Signal end of stream
        audio_queue.put(None)

    def _transcribe_chunk(self, audio_file: str) -> list:
        """Transcribe an audio chunk and return segments."""
        import mlx_whisper

        model_name = self.model_map.get(self.model_size, 'mlx-community/whisper-base')

        try:
            result = mlx_whisper.transcribe(
                audio_file,
                path_or_hf_repo=model_name,
                language=self.language,
            )
            return result.get('segments', [])
        except Exception as e:
            logging.error(f"Transcription error: {e}")
            return []

    def fetch_live_captions(self, video_id: str, flush_interval: int = 60) -> None:
        """
        Fetch and transcribe live captions from a YouTube stream.

        Args:
            video_id: YouTube video ID
            flush_interval: How often to flush CSV to disk (seconds)
        """
        self._stop_event.clear()

        timestamp = datetime.now(self.eastern).strftime("%Y%m%d_%H%M%S")
        filename = f"captions_{video_id}_{timestamp}.csv"

        logging.info(f"Starting caption capture for video: {video_id}")
        logging.info(f"Output file: {filename}")
        logging.info(f"Model: {self.model_size}, Language: {self.language}")
        logging.info(f"Chunk duration: {self.chunk_duration}s")
        logging.info("Press Ctrl+C to stop\n")

        # Pre-load model by doing a test transcription
        logging.info("Loading Whisper model (this may take a moment on first run)...")
        import mlx_whisper
        model_name = self.model_map.get(self.model_size, 'mlx-community/whisper-base')

        audio_queue = queue.Queue(maxsize=5)
        last_flush_time = time.time()
        termination_reason = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Start audio streaming thread
            audio_thread = threading.Thread(
                target=self._stream_audio_chunks,
                args=(video_id, temp_dir, audio_queue),
                daemon=True,
            )
            audio_thread.start()

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp (ET)', 'Start', 'End', 'Text'])

                try:
                    while True:
                        try:
                            item = audio_queue.get(timeout=self.chunk_duration + 15)
                        except queue.Empty:
                            logging.warning("Audio queue timeout, checking stream...")
                            if not audio_thread.is_alive():
                                termination_reason = "Audio stream ended"
                                break
                            continue

                        if item is None:
                            termination_reason = "Stream ended"
                            break

                        chunk_file, chunk_start_time = item

                        # Transcribe the chunk
                        segments = self._transcribe_chunk(chunk_file)

                        for segment in segments:
                            # Calculate actual timestamp
                            seg_start = segment.get('start', 0)
                            seg_end = segment.get('end', 0)
                            segment_time = chunk_start_time + timedelta(seconds=seg_start)
                            timestamp_str = segment_time.strftime('%Y-%m-%d %H:%M:%S %Z')

                            text = segment.get('text', '').strip()
                            if text:
                                print(f"{timestamp_str}: {text}")
                                writer.writerow([
                                    timestamp_str,
                                    f"{seg_start:.2f}",
                                    f"{seg_end:.2f}",
                                    text,
                                ])

                        # Clean up chunk file
                        try:
                            os.remove(chunk_file)
                        except OSError:
                            pass

                        # Periodic flush
                        current_time = time.time()
                        if current_time - last_flush_time >= flush_interval:
                            f.flush()
                            last_flush_time = current_time

                except KeyboardInterrupt:
                    logging.info("\nInterrupted by user.")
                    termination_reason = "Interrupted by user"
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    termination_reason = f"Error: {e}"
                finally:
                    self._stop_event.set()

                    if termination_reason:
                        writer.writerow(['Termination Reason:', termination_reason, '', ''])
                    f.flush()

                    logging.info(f"\nCaption log saved to {filename}")

        # Wait for audio thread to finish
        audio_thread.join(timeout=5)


def print_dependency_instructions(status: dict) -> None:
    """Print installation instructions for missing dependencies."""
    print("\nMissing dependencies:")

    if not status['yt-dlp']:
        print("\n  yt-dlp: pip install yt-dlp")

    if not status['ffmpeg']:
        print("\n  ffmpeg:")
        print("    macOS:   brew install ffmpeg")
        print("    Ubuntu:  sudo apt install ffmpeg")
        print("    Windows: https://ffmpeg.org/download.html")

    if not status['mlx-whisper']:
        print("\n  mlx-whisper: pip install mlx-whisper")
        print("    (Optimized for Apple Silicon Macs)")

    print()


def main():
    # Check dependencies
    status = check_dependencies()
    missing = [k for k, v in status.items() if not v]

    if missing:
        print("Error: Missing required dependencies")
        print_dependency_instructions(status)
        sys.exit(1)

    # Model selection
    print("Whisper model sizes (runs on Apple Silicon GPU):")
    print("  tiny   - Fastest, least accurate")
    print("  base   - Good balance [default]")
    print("  small  - Better accuracy")
    print("  medium - High accuracy")
    print("  large-v3 - Best accuracy (requires more memory)")
    print()

    model_size = input("Enter model size [base]: ").strip().lower() or "base"

    # Language
    language = input("Enter language code [en]: ").strip().lower() or "en"

    # Chunk duration
    chunk_input = input("Enter chunk duration in seconds [10]: ").strip()
    chunk_duration = int(chunk_input) if chunk_input else 10

    # Video URL/ID
    url_input = input("Enter YouTube URL or video ID: ").strip()
    video_id = extract_video_id(url_input)

    print(f"\nExtracted video ID: {video_id}")
    print(f"Model: {model_size}, Language: {language}, Chunk: {chunk_duration}s")
    print()

    # Create fetcher and start
    fetcher = LiveCaptionFetcher(
        model_size=model_size,
        language=language,
        chunk_duration=chunk_duration,
    )

    fetcher.fetch_live_captions(video_id)


if __name__ == "__main__":
    main()
