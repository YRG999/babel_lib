from typing import List
from yt_dlp import YoutubeDL

class YouTubeDownloader:
    def __init__(self, use_cookies: bool = False, download_comments: bool = False, comments_only: bool = False):
        self.filenames = []
        self.use_cookies = use_cookies
        self.download_comments = download_comments
        self.comments_only = comments_only

    def _progress_hook(self, d):
        if d['status'] == 'finished':
            filename = d.get('filename')
            if filename:
                self.filenames.append(filename)
                print(f"Finished downloading: {filename}")

    def download_video_info_comments(self, urls: List[str]) -> List[str]:
        ydl_opts = {
            'progress_hooks': [self._progress_hook],
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
        }

        if self.comments_only:
            ydl_opts['extract_flat'] = True
            ydl_opts['getcomments'] = True
            ydl_opts['skip_download'] = True
            ydl_opts['writeinfojson'] = True
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'live_chat'],
                'writedescription': True,
                'writeinfojson': True,
            })
            if self.download_comments:
                ydl_opts['getcomments'] = True

        if self.use_cookies:
            ydl_opts['cookiesfrombrowser'] = ('firefox',)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                for url in urls:
                    print(f"Processing: {url}")
                    ydl.download([url])
            return self.filenames
        except Exception as e:
            print(f"Error: {e}")
            return []