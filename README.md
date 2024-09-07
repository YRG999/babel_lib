# BABEL_LIB

Named after the [Library of Babel](https://libraryofbabel.info/) website. This started as an experiment in randomness but now hosts a bunch of experimental programs. I got help from [chatGPT](https://chat.openai.com/), [Claude AI](https://claude.ai/), and [Bard](https://bard.google.com/) to write some of them.

- [Setup](#setup)
- [Run](#run)
- [Other programs](#other-programs)
- [Wordplay](#wordplay)
- [Games](#games)
- [YouTube downloaders](#youtube-downloaders)
- [More](#more)

## Setup

For initial setup, create a virtual environment & run it:

```bash
$ python -m venv venv
$ . venv/bin/activate
```

Then install requirements:


```shell
$ pip install -r requirements.txt
```

After the initial setup & requirements, you only have to run the second venv line to activate the virtual environment when running in the future.

## Run

To run experiments, type `python` and the file name. For example, try this one:

```shell
$ cd ytdownload
$ python youtube_downloader.py
```

## Other programs

* `business_assumptions.py` - calculate breakeven cost and amount of drivers needed for a hypothetical future business idea.
* `gnews_scraper.py` - Scrape the latest 5 Google News headlines based on `h4` top stories.
* `lat_long.py` - find latitude & longitude.
* `moviesearch.py` - prints number of movies released in a range of years.
* `news_scraper.py` - BBC and NY Times headline scraper. Adapted [Indently's BBC News Headline scraper](https://www.youtube.com/watch?v=zo7yzIVpIJo) to scrape BBC news and New York Times headlines.
* `repeated_multiplication.py` - repeatedly multiply numbers.
* `retirement_calc.py` - calculate retirement.
* `wiki_articles.py` - Display the 10 most recently-updated articles.
* `write_key.py` - asks for a key and value and adds it to a dictionary. If the dictionary doesn't exist, creates it.

## Wordplay

* `count_letters.py` - Count letters in a word.
* `define_word.py` - Define a word.
* `entername.py` - Enter your name and get greeted with the current time.
* `gen_pass.py` - Generate passphrase. Uses the `https://random-word-api.herokuapp.com/word` API endpoint to generate a passphrase.
* `gensen_worddict.py` - Expanded `random_sentence.py`. Pulls random words from the `https://random-word-api.herokuapp.com/word` API endpoint and strings them together to create a sentence, then verifies the sentence against the `language_tool_python` API.
* `givename.py` - Runs `entername.py` and passes in a hardcoded name.
* `random_phrase.py` - (Buggy) Generate random phrase.
* `random_sentence_save.py` - Same as `random_sentence.py` except saves to file.
* `word_or_phrase.py` - Asks if you want to generate a random phrase or define a word.

## Games

* `dice_game.py` - experimental treasure hunt game.
* `dice_roll_anysided` - Roll a die with the number of sides specified by the user.
* `dice_rolls.py` - Rolls 2 6-sided dice.
* `die_roll_games.py` - 3 games
  1. Choose the number of sides for the die and roll it.
  2. Add to game 1 & see how many rolls it takes to roll the number again.
  3. Play game 2 a number of times.
* `die_roll_probability.py` - guess how many rolls it will take for game 2 (work in progress)
* `die-roll-histogram` - roll a die and generate a histogram of the values.
* `squid_game.py` - red light green light sim.

## YouTube downloaders

- `ytdownload/analyze_chat.py` - Analyze a youtube live chat CSV output by `youtube_downloader.py`.
- `ytdownload/extract_functions.py` - Extract functions used by `youtube_downloader.py`.
- `ytdownload/youtube_downloader.py` - Updated downloader using classes to download video, description, transcript, comments, and live chat and convert comments & live chat to CSV.

These use the `yt_dlp` [`YoutubeDL` Python class](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L191) or [embedded CLI](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) to download videos. You may want to install [`ffmpeg`](https://trac.ffmpeg.org/wiki/CompilationGuide/macOS) to handle some video conversion. Easiest way on macOS is through homebrew: `brew install ffmpeg`.

***See [Using yt-dlp cookies](more/Using_yt-dlp_cookies.md) for how to download a video from X/Twitter***

### YouTube Live fetcher

To save live video and chat:

1. Copy the VIDEO_ID, which is the final segment in a YouTube URL, for example, `ABC123` in `https://www.youtube.com/watch?v=ABC123`

2. In one window, run the following to download the live video from the start:

```sh
yt-dlp --live-from-start VIDEO_ID
```

3. In another window, run the following to download the live chat:

```sh
python youtube-live-chat-fetcher.py
```

4. Enter the VIDEO_ID in the input field.

### Other download options

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

### Youtube live chat fetcher

- `ytdownload/youtube-live-chat-fetcher.py` - Fetch live chat during a live stream. Requires API key.
- Sign up to develop with the [Google Cloud Platform](https://console.cloud.google.com/), create a project, and activate the YouTube Data API v3.
- Create an `.env` file with `YOUTUBE_API_KEY=yourapikey` and `MAPS_API_KEY=yourmapsapikey`.

## More

See [Programming notes](more/Programming_notes.md).
