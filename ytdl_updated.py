# Use this file to download YouTube videos
# (working name download_cmv)

from yt_dlp import YoutubeDL
from youtube_functions import *
from extract_functions import *

filenames = []

def progress_hook(d):
  if d['status'] == 'finished':
    filenames.append(d['filename'])

def download_video_info_comments(URLS):
    '''
    Download video, description, live_chat, comments (info), transcript (en.vtt).
    
    Return list of live_chat, en.vtt, and media files.
    '''
    
    ydl_opts = {
       'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
       'getcomments': True,                    # Extract video comments; requires writeinfojson to write to disk
       'writesubtitles': True,                 # Write subtitles to a file
       'writeautomaticsub': True,              # Write automatic subtitles
       'subtitleslangs': ['en','live_chat'],   # Write English transcript ('en') and live chat
       'writedescription': True,               # Write description to file
       'writeinfojson': True,                  # Write the video description (and comments) to a .info.json file
       'progress_hooks': [progress_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        for url in URLS:
            ydl.download(url)

    return filenames

def return_transcript_files(filenames):
    '''
    Iterate through list of filenames and return transcript file names.
    '''
    # Create an empty list to store the transcript files    
    transcript_files = []

    # Iterate over the list of files
    for file in filenames:
        # Check if the file name ends with ".en.vtt"
        if file.endswith(".en.vtt"):
            # Save the file to a variable
            transcript_files.append(file)

    # Return the list of transcript files
    return transcript_files

def return_livechat_files(filenames):
    '''
    Iterate through list of filenames and return live_chat file names.
    '''
    # Create an empty list to store the livechat files
    livechat_files = []

    # Iterate over the list of files
    for file in filenames:
        # Check if the file name ends with ".live_chat.json"
        if file.endswith(".live_chat.json"):
            # Save the file to the list
            livechat_files.append(file)

    # Return the list of livechat files
    return livechat_files

def get_filenames(extension):
    '''
    Scan the directory for the file with the specified extension.
    
    Parameters:
    - extension: The file extension to search for (e.g., 'live_chat.json').
    
    Returns:
    - The filename of the file with the specified extension.
    - None if no such file is found.
    '''
    for filename in os.listdir('.'):
        if filename.endswith(extension):
            return filename
    return None

def return_comment_files():
    '''
    Iterate through list of filenames and return comment file names.
    '''
    comment_filenames = []
    comment_filenames.append(get_filenames('info.json'))
    return comment_filenames

def livechat_to_csv(json_path):
    '''
    Convert live_chat JSON file to CSV.
    '''
    data_list = []
    
    # Load each JSON object separately, ignoring whitespace between them
    with open(json_path, 'r') as json_file:
        decoder = json.JSONDecoder()
        file_content = json_file.read()
        idx = 0
        while idx < len(file_content):
            try:
                obj, idx = decoder.raw_decode(file_content, idx)
                data_list.append(obj)
            except json.JSONDecodeError:
                idx += 1  # Skip over any whitespace or unexpected characters
    
    # Extract required data
    extracted_data = []
    for data in data_list:
        actions = data.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            item = action.get('addChatItemAction', {}).get('item', {}).get('liveChatTextMessageRenderer', {})
            message = extract_text_and_emoji(item)
            authorname = extract_authorname(item)
            timestamp = extract_timestamp(item)
            eastern_time = convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            extracted_data.append([message, authorname, eastern_time])
    
    # Write to CSV
    csv_path = json_path+".csv"
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Message", "AuthorName", "Eastern Time"])
        writer.writerows(extracted_data)

    return csv_path

def comment_to_csv(comment_file):
    '''
    Convert comment JSON file to CSV.
    '''
    # Read the JSON comment file
    with open(comment_file, 'r') as file:
        data = json.load(file)

    # Traverse the JSON data
    comments = data['comments']
    extracted_data = []
    for comment in comments:
        comment_id = comment['id']
        text = comment['text']
        author = comment['author']
        timestamp = comment['timestamp']
        eastern_time = convert_to_eastern(timestamp)
        extracted_data.append([comment_id, text, author, timestamp, eastern_time.strftime('%Y-%m-%d %H:%M:%S')])

    # Write to CSV
    comment_csv = comment_file+".csv"
    with open(comment_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Comment ID', 'Text', 'Author', 'Timestamp', 'Eastern Time'])
        writer.writerows(extracted_data)

    return comment_csv

if __name__ == "__main__":
    # Download URLs: video, description, live_chat, info (comments), transcript (en.vtt)
    # Save transcript to text, live_chat and comments to CSV.

    urls = get_video_url()
    filenames = download_video_info_comments([urls])

    transcript_files = return_transcript_files(filenames)
    for file in transcript_files:
        clean_filename = clean_transcript(file)
        print(f"Transcript saved as: {clean_filename}")

    livechat_files = return_livechat_files(filenames)
    for file in livechat_files:
        livechat_csv = livechat_to_csv(file)
        print(f"Live chat saved as: {livechat_csv}")

    comment_files = return_comment_files()
    for file in comment_files:
        comment_csv = comment_to_csv(file)
        print(f"Comments saved as: {comment_csv}")
