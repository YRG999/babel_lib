# BABEL_LIB

This is called BABEL_LIB after the [Library of Babel](https://libraryofbabel.info/) website. It started as an experiment in randomness but now hosts a bunch of experimental programs. I used chatGPT to help me write some of them.

## Experiments

1. `random_sentence.py` - creates random "words" and sentences. See `gensen_worddict.py` for further explorations
2. `random_sentence_save.py` - sames as above, except saves to file.
3. `dice_roles.py` - rolls 2 6-sided dice.
4. `wiki_articles.py` - displays the 10 most recently-updated articles.
5. `your_youtube.py` - displays the 10 most recently-added YouTube videos.
6. `youtube_search_loc.py` - displays the 10 most recently-added YouTube videos in a specific location.
7. `lat_long.py` - Displays the latitude and longitude for an address. Uses the Google Maps API.
8. `yt_loc2.py` - User-friendly YouTube search by location.
9. `gnews_scraper.py` - Scrape the latest 5 Google News headlines based on `h4` top stories.
10.  `gensen_worddict.py` - Expanded `random_sentence.py`. Pulls random words from the `https://random-word-api.herokuapp.com/word` API endpoint and strings them together to create a sentence, then verifies the sentence against the `language_tool_python` API.
11. `gen_pass.py` - Generate passphrase. Uses the `https://random-word-api.herokuapp.com/word` API endpoint to generate a passphrase.
12. `news_scraper` - BBC and NY Times headline scraper. Adapted [Indently's BBC News Headline scraper](https://www.youtube.com/watch?v=zo7yzIVpIJo) to scrape BBC news and New York Times headlines.
13. `dlvideo.py` - Download YouTube, TikTok, and other videos from URL using `yt_dlp`.
14. `ytdlchatvidthreads.py` - Download YouTube Live video and chat.
15. ~~`readmultijson.py` - Extract message and username from YouTube Live chat JSON file.~~
16. `commentdl.py` - Download comments from YouTube video and automatically runs `extractcomments.py`.
17. `extractcomments.py` - Extract comments from JSON file into CSV.
18. `entername.py` - Enter your name and get greeted with the current time.
19. `givename.py` - Runs `entername.py` and passes in a hardcoded name.
20. Replaced `readmultijson.py` with `main_extraction.py` and `extract_functions.py` to separate functions and add emoji and timestamps.

## Setup

For initial setup, create a virtual environment & run it:

```bash
$ python -m venv venv
$ . venv/bin/activate
```

Then install requirements:

```shell
pip install -r requirements.txt
```

In subsequent setups, just run the second venv line to activate the virtual environment.

## YouTube and Geolocation Requirements

*Required for apps 5-8*

* Sign up to develop with the [Google Cloud Platform](https://console.cloud.google.com/), create a project, and activate the YouTube Data API v3 and the Geocoding API.
* Create an `.env` file with `YOUTUBE_API_KEY=yourapikey` and `MAPS_API_KEY=yourmapsapikey`.

## `dlvideo.py` options

*Suggested for apps 13-15*

* Programs using [`yt_dlp`](https://github.com/yt-dlp/yt-dlp), such as `randtube` & `rectube` - you should install `ffmpeg`. Easiest way on macOS is through homebrew: `brew install ffmpeg` See for more: https://trac.ffmpeg.org/wiki/CompilationGuide/macOS.

```python
# other options
ydl_opts = {
  'listformats': True, # list available formats
}

ydl_opts = {
  'format' : '00' # enter format ID
  'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
}

ydl_opts = {
  'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]', # download up to 720p video
  'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
}
```

## Programming notes & links

* Had some trouble setting the environment variable using the `.env` file. [3](https://stackoverflow.com/questions/40728259/updated-environment-variable-but-os-getenv-keeps-returning-none) [4](https://www.php.net/manual/en/function.getenv.php) [5](https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5) [6](https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs) 
* [requests](https://pypi.org/project/requests/) - doc for the python HTTP requests library, which makes it easy to send requests in python.
* [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started) - this is the API I used for search; v3.
* [Search:list location](https://developers.google.com/youtube/v3/docs/search/list#location) - Helped with `yt_loc2.py` error. It said I needed to add the `locationRadius` as well.
* [Request contains an invalid argument Location paramter \[sic\] Youtube API ](https://stackoverflow.com/questions/72883738/request-contains-an-invalid-argument-location-paramter-youtube-api) - This helped me troubleshoot errors I was having with sending an invalid location parameter. Prior to this, I didn't know how to specify the latitude and longitude. I had been sending it as `(lat,long)` with the parentheses, but this answer showed that I should not use that.
* Run `pip list` to list installed packages.
* [Git keeps asking me for my ssh key passphrase](https://stackoverflow.com/questions/10032461/git-keeps-asking-me-for-my-ssh-key-passphrase) - helpful tip.
