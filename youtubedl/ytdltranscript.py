# Download YouTube video transcripts
# Uses code from ytdl_updated.py

from ytdl_updated import * 

def download_transcript(URLS):
    '''
    Download transcript (en.vtt) & return clean txt file.
    '''
    
    ydl_opts = {
    #    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    #    'getcomments': True,                    # Extract video comments; requires writeinfojson to write to disk
    #    'writesubtitles': True,                 # Write subtitles to a file
       'writeautomaticsub': True,              # Write automatic subtitles
    #    'subtitleslangs': ['en','live_chat'],     # Write English transcript ('en') and live chat
       'skip_download': True,                    # Don't download the video
    #    'writedescription': True,               # Write description to file
    #    'writeinfojson': True,                  # Write the video description (and comments) to a .info.json file
       'progress_hooks': [progress_hook]
    }

    with YoutubeDL(ydl_opts) as ydl:
        for url in URLS:
            ydl.download(url)

    return filenames

def download_and_clean_transcript():
    urls = get_video_url()
    filenames = download_transcript([urls])

    transcript_files = return_transcript_files(filenames)
    for file in transcript_files:
        clean_filename = clean_transcript(file)
        print(f"Transcript saved as: {clean_filename}")

def main():
    download_and_clean_transcript()

if __name__ == "__main__":
    main()