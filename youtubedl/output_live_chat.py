# output_live

import subprocess
import json

def stream_live_chat(video_url):
    # Command to extract live chat using yt-dlp
    command = [
        'yt-dlp',
        '--no-warnings',
        '--skip-download',
        '--print', 'json',
        '-o-',  # Output to stdout
        '--',  # End of options
        video_url
    ]

    # Start the subprocess to run yt-dlp
    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, universal_newlines=True) as proc:
        for line in proc.stdout:
            try:
                chat_data = json.loads(line.strip())
                print_chat_message(chat_data)
            except json.JSONDecodeError:
                continue

def print_chat_message(chat_data):
    # Customize how chat messages are displayed
    print(f"{chat_data['author']['name']}: {chat_data['message']}")

if __name__ == "__main__":
    # video_url = 'YOUR_VIDEO_URL_HERE'  # Place your YouTube live video URL here
    video_url = input("Enter the YouTube live video URL: ")
    stream_live_chat(video_url)
