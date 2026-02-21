# BABEL_LIB

Named after the [Library of Babel](https://libraryofbabel.info/) website. This started as an experiment in randomness but now hosts a bunch of experimental programs. I got help from [chatGPT](https://chat.openai.com/), [Claude AI](https://claude.ai/), and [Gemini](https://gemini.google.com/), and [Github CoPilot](https://github.com/copilot) to write them.

- [Quick start](#quick-start)
- [Setup](#setup)
- [Run](#run)
- [encodeDecodeImage](#encodedecodeimage)
- [Games](#games)
- [Other](#other)
- [Radius](#radius)
- [Wordplay](#wordplay)
- [YouTube downloaders](#youtube-downloaders)
- [Additional documentation](#additional-documentation)

## Quick start

The most updated files are the two main YouTube downloaders:

- **Modern downloader CLI** – `youtube-downloader-app/src/main.py`
- **Live chat–focused CLI** – `ytdownload/livechat.py`

These both wrap `yt-dlp` under the hood to download videos and/or live chats.

### 1. Modern downloader CLI (`youtube-downloader-app/src/main.py`)

Requirements:

- Python virtualenv activated and dependencies installed (see [Setup](#setup)).
- `yt-dlp` installed (already in `requirements.txt`).

Run:

```zsh
cd youtube-downloader-app
python src/main.py
```

Then:

1. Paste a YouTube URL when prompted.
2. Choose whether to use cookies, download comments, transcripts, etc.
3. Let the script download the video and any selected extras into the output folder.

See [youtube-downloader-app README](/youtube-downloader-app/README.md) for more details and advanced options.

### 2. Live chat–focused CLI (`ytdownload/livechat.py`)

This script is optimized for grabbing live chat (and optionally video) for live streams.

Requirements:

- Python virtualenv activated and dependencies installed.
- `yt-dlp` installed.
- (Optional but recommended) `ffmpeg` installed for robust video merging:

  ```zsh
  brew install ffmpeg
  ```

Run:

```zsh
cd ytdownload
python livechat.py
```

Then:

1. Enter the YouTube `VIDEO_ID` (the part after `v=` in the URL).
2. Follow the prompts to start fetching live chat and/or video.
3. Monitor progress in the terminal; output files (CSV, video) will be written into the current folder.

If you hit authentication or region errors, see [Using yt-dlp cookies](_doc/Using_yt-dlp_cookies.md) and the [YouTube downloaders](#youtube-downloaders) section below for cookie and browser-based login examples.

## Setup

For initial setup, create a virtual environment & run it:

```zsh
python -m venv venv
. venv/bin/activate
```

Then install requirements:

```zsh
pip install -r requirements.txt
```

After the initial setup & requirements, you only have to run the second venv line to activate the virtual environment when running in the future.

### Upgrade yt-dlp

If necessary you may need to upgrade `yt-dlp`. For example, if you see "The following content is not available on this app" or similar errors when running `yt-dlp --live-from-start -- video_id`

Check version.

```zsh
yt-dlp --version
```

Install upgrade.

```zsh
pip install yt-dlp --upgrade
```

Or

```zsh
pip install -U yt-dlp
```

## Run

To run experiments, type `python` and the file name. For example, try this one:

```zsh
cd ytdownload
python youtube_downloader.py
```

## encodeDecodeImage

Code that encodes text into an image using simple least-significant-bit (LSB) steganography, and decodes it back.

- `create_image.py` – Creates an image of a blue cirle with a white background. Defines circle parameters, draws the circle, and saves the image. Useful for generating a clean base image to encode into.
- `encode_image.py` – Converts text to binary and encodes the bits into the RGB pixel values of an image, saving the result as `encoded_image.png`.
- `decode_image.py` – Reads pixel data from `encoded_image.png`, reconstructs the hidden binary data, converts it back to text, and prints the decoded message (or reports that no hidden message was found).
- `encode_decode_image.md` – Walkthrough and explanation of how the encoding/decoding works using PIL (`Pillow`) and LSB manipulation; serves as conceptual documentation for this mini‑project.
- `original_image.png` – Example unencoded source image used as the input to the encoding script.
- `encoded_image.png` – Example output image containing hidden text data produced by the encoding script.

## Games

- `dice_game.py` - experimental treasure hunt game.
- `dice_roll_anysided` - Roll a die with the number of sides specified by the user.
- `dice_rolls.py` - Rolls 2 6-sided dice.
- `die_roll_games.py` - 3 games
  - Choose the number of sides for the die and roll it.
  - Add to game 1 & see how many rolls it takes to roll the number again.
  - Play game 2 a number of times.
- `die_roll_probability.py` - guess how many rolls it will take for game 2 (work in progress)
- `die-roll-histogram` - roll a die and generate a histogram of the values.
- `squid_game.py` - red light green light sim.

## Other

- `business_assumptions.py` - calculate breakeven cost and amount of drivers needed for a hypothetical future business idea.
- `gnews_scraper.py` - Scrape the latest 5 Google News headlines based on `h4` top stories.
- `lat_long.py` - find latitude & longitude.
- `life.html` - Interactive artificial-life “soup” simulation (Tierra‑Lite v2) running entirely in the browser.
- `lifetime-metrics.html` - Lifetime metrics calculator; lets you explore how many hours you’ve spent on sleep, work, commuting, etc. given your habits.
- `moviesearch.py` - prints number of movies released in a range of years.
- `news_scraper.py` - BBC and NY Times headline scraper. Adapted [Indently's BBC News Headline scraper](https://www.youtube.com/watch?v=zo7yzIVpIJo) to scrape BBC news and New York Times headlines.
- `random_tarot.py` - Draw a random Major Arcana tarot card and show its meaning.
- `repeated_multiplication.py` - repeatedly multiply numbers.
- `retirement_calc.py` - calculate retirement.
- `savings_calc.py` - Calculate and export a 12‑month interest table for a savings account (principal, APY, monthly interest, and running balance).
- `timeline.py` - Generate a horizontal timeline PNG for a date range, with start/end labels, equidistant tick marks, and today highlighted if it falls inside the range.
- `wiki_articles.py` - Display the 10 most recently-updated articles.
- `word_count.py` - Count how many times a target word appears in a text file.
- `write_key.py` - asks for a key and value and adds it to a dictionary. If the dictionary doesn't exist, creates it.

## Radius

- `radius_notes.md` - Notes and step‑by‑step instructions for building a “draw a radius on a map” tool using Google Maps APIs and `folium`, including setup, code samples, and troubleshooting (e.g., `REQUEST_DENIED` / billing).
- `radius.py` - Python script that geocodes a hardcoded address (Empire State Building) with Google Maps, then uses `folium` to generate an HTML map (`map_with_radius.html`) showing a 1 km radius circle around the location.

## Wordplay

- `count_letters.py` - Count letters in a word.
- `define_word.py` - Define a word.
- `entername.py` - Enter your name and get greeted with the current time.
- `gen_pass.py` - Generate passphrase. Uses the `https://random-word-api.herokuapp.com/word` API endpoint to generate a passphrase.
- `gensen_worddict.py` - Expanded `random_sentence.py`. Pulls random words from the `https://random-word-api.herokuapp.com/word` API endpoint and strings them together to create a sentence, then verifies the sentence against the `language_tool_python` API.
- `givename.py` - Runs `entername.py` and passes in a hardcoded name.
- `random_phrase.py` - (Buggy) Generate random phrase.
- `random_sentence_save.py` - Same as `random_sentence.py` except saves to file.
- `word_or_phrase.py` - Asks if you want to generate a random phrase or define a word.

## YouTube downloaders

`youtube-downloader-app` is the more modern downloader to download videos and past livestreams including transcripts, comments, and live chat. `ytdownload` is the older version that is still useful for downloading livestreams. See [`python livechat.py`](#livechat-downloader) for details.

These use the `yt_dlp` [`YoutubeDL` Python class](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L191) or [embedded CLI](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) to download videos. You may want to install [`ffmpeg`](https://trac.ffmpeg.org/wiki/CompilationGuide/macOS) to handle some video conversion. Easiest way on macOS is through homebrew: `brew install ffmpeg`.

### youtube-downloader-app

Usage:

1. Run the application:

   ```zsh
   python src/main.py
   ```

2. Follow the prompts to enter the YouTube URL and choose your options regarding cookies and comments.

See [youtube-downloader-app README](/youtube-downloader-app/README.md) for more details.

### ytdownload

- `ytdownload/analyze_chat.py` - Analyze a youtube live chat CSV output by `youtube_downloader.py`.
- `ytdownload/extract_functions.py` - Extract functions used by `youtube_downloader.py`.
- `ytdownload/youtube_downloader.py` - Updated downloader using classes to download video, description, transcript, comments, and live chat and convert comments & live chat to CSV.

### livechat downloader

To save live video and chat:

1. Copy the VIDEO_ID, which is the final segment in a YouTube URL, for example, `ABC123` in `https://www.youtube.com/watch?v=ABC123`.

2. Run the following to download the live chat:

    ```zsh
    python youtube-live-chat-fetcher.py
    ```

3. Enter the VIDEO_ID in the input field.

4. Copy the code to download the live video from the start and run it in a new terminal:

    ```zsh
    yt-dlp --live-from-start -- VIDEO_ID
    ```

#### cookies

If you get the error:

```zsh
ERROR: [youtube] URL: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
```

Sign in with firefox then try:

```zsh
yt-dlp --cookies-from-browser firefox --live-from-start -- URL
```

### Pass input from terminal

<https://superuser.com/questions/1409426/how-to-pass-input-to-a-script-from-terminal>

The following will start the program and begin downloading the `VIDEO_ID` provided in the link.

`printf '%s\n' "https://www.youtube.com/watch?v=VIDEO_ID" | python youtube_downloader.py`

### Twitter/x.com videos

To download using a guest token, use `yt-dlp X_URL`.

If you get the error "file name too long", use the following:

```zsh
yt-dlp -o "%(id)s.%(ext)s" X_URL
```

See more [Porteus forum discussion](https://forum.porteus.org/viewtopic.php?t=10408), [yt-dlp issue #5060](https://github.com/yt-dlp/yt-dlp/issues/5060), and [yt-dlp issue #1136](https://github.com/yt-dlp/yt-dlp/issues/1136).

***See [Using yt-dlp cookies](more/Using_yt-dlp_cookies.md) if you need to log in to download***

### Instagram stories

Use `yt-dlp --cookies-from-browser firefox URL`.

See <https://github.com/yt-dlp/yt-dlp/issues/8290#issuecomment-1753826148>.

### Kick

Simple option:

```zsh
yt-dlp <kick_replay_url>
```

Previous option (if the above doesn't work, this is the old way):

[how-to-download-your-kick-replays](https://help.kick.com/en/articles/7832538-how-to-download-your-kick-replays)

1. Open your browser and press F12
2. Click the "Network" tab
3. Load the replay in your browser
4. In the network tab, search for m3u8
5. Right Click the file master.m3u8 and select Copy URL
6. Open your command line / terminal
7. If on Windows, go to the directory where the yt-dlp file has been installed
8. Run the following Command: ​`​yt-dlp <kick_replay_url>`

### merge files

Merge downloaded fragments with ffmpeg’s concat demuxer.

1. Create a file named filelist.txt with the files listed in order.

    ```txt
    file 'filename.f137.mp4.part'
    file 'filename.f140.mp4.part'
    ```

2. Run the ffmpeg command to merge them:

    ```zsh
    ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
    ```

This will merge the fragments into output.mp4.

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

### Terminal commands

List formats

```zsh
yt-dlp -F "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download best video and audio at the highest resolution

```zsh
yt-dlp -f "bestvideo+bestaudio/best" "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Youtube live chat fetcher

- `ytdownload/youtube-live-chat-fetcher.py` - Fetch live chat during a live stream. Requires API key.
- Sign up to develop with the [Google Cloud Platform](https://console.cloud.google.com/), create a project, and activate the YouTube Data API v3.
- Create an `.env` file with `YOUTUBE_API_KEY=yourapikey` and `MAPS_API_KEY=yourmapsapikey`.

## Additional documentation

- [chatGPT_documentation.md](_doc/chatGPT_documentation.md)
- [Claude_debugging.md](_doc/Claude_debugging.md)
- [mistral20240725.md](_doc/mistral20240725.md)
- [Programming_notes.md](_doc/Programming_notes.md)
- [Using_yt-dlp_cookies.md](_doc/Using_yt-dlp_cookies.md)
