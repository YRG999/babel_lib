# ytdl_livechat.py
# NEED TO DEBUG

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

# TRYING TO INTEGRATE NEW LIVECHAT FUNCTIONS
# getting error:
# actions = data.get('replayChatItemAction', {}).get('actions', [])
# AttributeError: 'bool' object has no attribute 'get'
# I was able to fix this before in ytdl_updated.py, but don't remember how
def download_livechat_to_csv():
    '''
    Run download_livechat function and convert live_chat file to csv.
    
    Return live_chat file and live_chat.json.csv file.
    '''

    # # Download livechat & convert to CSV.
    # urls = get_video_url()
    # livechat = download_livechat([urls])
    # json_path = next((file for file in livechat if file.endswith('.json')), None)

    # ## check to see if there is a downloaded livechat JSON file
    # csv_path = json_path+".csv"  # Name CSV file by added extension to JSON file
    # data = extract_data_from_json(json_path) # Extract data from live_chat.json
    # write_to_csv(data, csv_path) # Write to live_chat.json.csv
    # print(f"Data written to '{csv_path}'") # Print the name of the CSV file to the console

    urls = get_video_url()
    livechat_files = download_livechat([urls])
    for file in livechat_files:
        # print("file = "+file)
        json_data, filename = get_json_data_auto(file)
        result = extract_data_from_json(json_data, filename)
        
        # Generate output filename based on input filename
        output_filename = os.path.splitext(filename)[0] + "_extracted.csv"
        
        save_to_csv(result, output_filename)

def main():
   download_livechat_to_csv()

if __name__ == "__main__":
   main()