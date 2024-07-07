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
    '''
    Run download_livechat function and convert live_chat file to csv.
    
    Return live_chat file and live_chat.json.csv file.
    '''

    urls = get_video_url()
    filenames = download_livechat([urls])

    livechat_files = return_livechat_files(filenames)
    for file in livechat_files:
        json_data, filename = get_json_data(file)
        result = extract_data_from_json(json_data, filename)
        
        # Generate output filename based on input filename
        output_filename = os.path.splitext(filename)[0] + "_extracted.csv"
        
        save_to_csv(result, output_filename)

def main():
   download_livechat_to_csv()

if __name__ == "__main__":
   main()