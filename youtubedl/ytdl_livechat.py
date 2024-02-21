# ytdl_livechat.py

from yt_dlp import YoutubeDL
from ytdl_updated import *

filenames = []

def progress_hook(d):
  if d['status'] == 'finished':
    filenames.append(d['filename'])

def download_livechat(URLS):
    '''
    Download live_chat.
    
    Return live_chat file.
    '''
    
    ydl_opts = {
       'skip_download': True,          # Don't download the video, just subtitles (live chat replay)
       'getcomments': False,           # Extract video comments; req writeinfojson to write to disk
       'writesubtitles': True,                 # Write subtitles to a file
       'writeautomaticsub': True,              # Write automatic subtitles
       'subtitleslangs': ['en','live_chat'],   # Write English transcript ('en') and live chat
       'writedescription': False,               # Write description to file
       'writeinfojson': False,         # Write video description (and comments) to a .info.json file
       'progress_hooks': [progress_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        for url in URLS:
            ydl.download(url)

    return filenames

def download_livechat_to_csv():
    # Download livechat & convert to CSV.
    urls = get_video_url()
    livechat = download_livechat([urls])
    json_path = next((file for file in livechat if file.endswith('.json')), None)

    ## check to see if there is a downloaded livechat JSON file
    csv_path = json_path+".csv"  # Name CSV file by added extension to JSON file
    data = extract_data_from_json(json_path) # Extract data from live_chat.json
    write_to_csv(data, csv_path) # Write to live_chat.json.csv
    print(f"Data written to '{csv_path}'") # Print the name of the CSV file to the console

def main():
   download_livechat_to_csv()

if __name__ == "__main__":
   main()