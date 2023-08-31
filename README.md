# BABEL_LIB

This is called BABEL_LIB after the [Library of Babel](https://libraryofbabel.info/) website. It started as an experiment in randomness but now hosts a bunch of experimental programs. I used chatGPT to help me write some of them.

- [Experiments](#experiments)
  - [Random](#random)
  - [Wikipedia \& news](#wikipedia--news)
  - [Google \& Youtube APIs](#google--youtube-apis)
  - [Youtube downloaders](#youtube-downloaders)
- [Setup](#setup)
- [YouTube and Geolocation Requirements](#youtube-and-geolocation-requirements)
- [`dlvideo.py` options](#dlvideopy-options)
- [More](#more)

## Experiments

List of maintained apps.

### Random

* `random_sentence.py` - Creates random nonsense words and sentences.
  * `gensen_worddict.py` - Expanded `random_sentence.py`. Pulls random words from the `https://random-word-api.herokuapp.com/word` API endpoint and strings them together to create a sentence, then verifies the sentence against the `language_tool_python` API.
  * `random_sentence_save.py` - Same as `random_sentence.py` except saves to file.
* `dice_roles.py` - Rolls 2 6-sided dice.
  * `dice_roll_anysided` - Roll a die with the number of sides specified by the user.
* `gen_pass.py` - Generate passphrase. Uses the `https://random-word-api.herokuapp.com/word` API endpoint to generate a passphrase.
* `entername.py` - Enter your name and get greeted with the current time.
  * `givename.py` - Runs `entername.py` and passes in a hardcoded name.

### Wikipedia & news

* `wiki_articles.py` - Display the 10 most recently-updated articles.
* `gnews_scraper.py` - Scrape the latest 5 Google News headlines based on `h4` top stories.
* `news_scraper` - BBC and NY Times headline scraper. Adapted [Indently's BBC News Headline scraper](https://www.youtube.com/watch?v=zo7yzIVpIJo) to scrape BBC news and New York Times headlines.

### Google & Youtube APIs

[*requirements*](#youtube-and-geolocation-requirements)

* `your_youtube.py` - Display the 10 most recently-added YouTube videos.
* `youtube_search_loc.py` - Display the 10 most recently-added YouTube videos in a specific location.
* `yt_loc2.py` - User-friendly YouTube search by location.
* `lat_long.py` - Display the latitude and longitude for an address. Uses the Google Maps API.

### Youtube downloaders

[*requirements*](#dlvideopy-options)

* `dlvideo.py` - ***(not just YouTube)*** Download YouTube, TikTok, and other videos from URL using `yt_dlp`.
* `ytdlchatvidthreads.py` - Download YouTube Live video and chat.
* `commentdl.py` - Download comments from YouTube video. Saves output as a JSON and CSV file. Depends on `youtube_functions.py`.
* `ytlivechatcommentdl.py` - Download YouTube live stream video, live chat, and comments. Extracts comments and live chat to CSV.
  * Consolidates `ytdlchatvidthreads.py`, `main_extraction.py` and `commentdl.py`.
  * Uses `youtube_functions.py` and `youtube_functions2.py`.
* `ytlive-chatextract.py` - Extract YouTube live chat from JSON to CSV.
* `ytdltranscript.py` - Download YouTube transcript and save cleaned version without timecodes to text file. Uses `youtube_functions.py`

#### Youtube downloader functions
* `youtube_functions.py` - Functions used in `ytlivechatcommentdt.py`, `commentdl.py`, and `ytdltranscript.py`.
* `youtube_functions2.py` - Used in `ytlivechatcommentdt.py` and `ytlive-chatextract.py`.
  * Uses `extract_functions.py`.

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

*Required for Google & Youtube API apps*

* Sign up to develop with the [Google Cloud Platform](https://console.cloud.google.com/), create a project, and activate the YouTube Data API v3 and the Geocoding API.
* Create an `.env` file with `YOUTUBE_API_KEY=yourapikey` and `MAPS_API_KEY=yourmapsapikey`.

## `dlvideo.py` options

*Suggested for Youtube downloaders*

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

## More

See [Programming notes](more/Programming_notes.md).