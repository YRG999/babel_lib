from typing import Any, List, cast
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
                # Do NOT force -f; let yt-dlp choose like the plain CLI.
                # Only force the final container to mp4, if possible.
                'merge_output_format': 'mp4',
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
            with YoutubeDL(cast(Any, ydl_opts)) as ydl:
                for url in urls:
                    print(f"Processing: {url}")
                    ydl.download([url])
            return self.filenames
        except Exception as e:
            print(f"Error: {e}")
            return []