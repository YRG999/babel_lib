import shutil
from typing import Any, List, cast
from yt_dlp import YoutubeDL

class YouTubeDownloader:
    def __init__(
        self,
        use_cookies: bool = False,
        download_comments: bool = False,
        metadata_only: bool = False,
        transcript_only: bool = False,
        comments_only: bool = False,
    ):
        self.filenames = []
        self.use_cookies = use_cookies
        self.download_comments = download_comments
        self.metadata_only = metadata_only
        self.transcript_only = transcript_only
        self.comments_only = comments_only

    def _progress_hook(self, d):
        if d['status'] == 'finished':
            filename = d.get('filename')
            if filename:
                self.filenames.append(filename)
                print(f"Finished downloading: {filename}")

    def _warn_if_missing_ffmpeg(self) -> None:
        if not shutil.which('ffmpeg'):
            print(
                "Warning: FFmpeg not found. yt-dlp may download separate audio/video "
                "streams and fail to merge them. Install FFmpeg to get a single "
                "audio+video file."
            )

    def download_video_info_comments(self, urls: List[str]) -> List[str]:
        skip_video = self.metadata_only or self.transcript_only or self.comments_only
        if not skip_video:
            self._warn_if_missing_ffmpeg()

        base_opts = {
            'progress_hooks': [self._progress_hook],
            'ignoreerrors': True,
            'remote_components': ['ejs:github'],
        }
        if self.use_cookies:
            base_opts['cookiesfrombrowser'] = ('firefox',)

        if self.comments_only:
            passes = [{
                **base_opts,
                'format': 'best',
                'skip_download': True,
                'writeinfojson': True,
                'getcomments': True,
            }]
        elif self.transcript_only:
            passes = [{
                **base_opts,
                'format': 'best',
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-AU'],
            }]
        elif self.metadata_only:
            metadata_opts = {
                **base_opts,
                'format': 'best',
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-AU', 'live_chat'],
                'writedescription': True,
                'writeinfojson': True,
            }
            if self.download_comments:
                metadata_opts['getcomments'] = True
            passes = [metadata_opts]
        else:
            # Two passes: the video first, then metadata + live chat. Within a
            # single pass yt-dlp downloads subtitles (including a potentially
            # slow live chat replay) before the video; downloading the video
            # first, immediately after its URLs are extracted, gives YouTube the
            # least room to reject them (HTTP 403) under its 2026 anti-download
            # enforcement.
            metadata_opts = {
                **base_opts,
                'format': 'best',
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-AU', 'live_chat'],
                'writedescription': True,
                'writeinfojson': True,
            }
            if self.download_comments:
                metadata_opts['getcomments'] = True
            video_opts = {
                **base_opts,
                # Prefer separate best video + best audio, and fall back to single-file best.
                'format': 'bv*+ba/best',
                # Test the selected format URLs before downloading and fall back
                # to other formats if they are outright dead. Note this cannot
                # catch YouTube's per-URL data cap (the test fetch is small and
                # succeeds even on URLs that later 403 mid-download).
                'check_formats': 'selected',
                # Only force the final container to mp4, if possible.
                'merge_output_format': 'mp4',
            }
            passes = [video_opts, metadata_opts]

        try:
            for ydl_opts in passes:
                with YoutubeDL(cast(Any, ydl_opts)) as ydl:
                    for url in urls:
                        print(f"Processing: {url}")
                        if ydl.download([url]) != 0:
                            print(f"Warning: yt-dlp reported errors for {url} — see output above.")
            return self.filenames
        except Exception as e:
            print(f"Error: {e}")
            return []