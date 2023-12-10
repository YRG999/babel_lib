# Programming notes

- [Experiments - more details](#experiments---more-details)
- [YouTube search](#youtube-search)
  - [Latitude and longitude](#latitude-and-longitude)
- [Programming notes \& links](#programming-notes--links)
  - [Git asks for SSH key \& passphrase](#git-asks-for-ssh-key--passphrase)
  - [YouTube \& Google APIs](#youtube--google-apis)
  - [Links](#links)
- [Additional resources](#additional-resources)
- [stash](#stash)

## Experiments - more details

*This list is no longer maintained.*

1. `random_sentence.py` - creates random "words" and sentences.
    - In the spirit of the library of babel, I wanted to create a program that would string together random words to create sentences. 
    - Ideally I wanted to recreate the library of babel site so that I could create books and eventually find one that made sense. 
    - But with infinity, there's infinite nothingness and chaos as well as everything that's ever existed and ever will be, so I abandoned this. 
    - I also thought about adding a dictionary so that only words that made sense would be output, but abandoned that too.
    - **Update:** see `gensen_worddict.py` for further explorations
2. `random_sentence_save.py` - same, except saves to file.
    - this is the same as the first one, except it saves the randomness to a file instead of outputting it in the console.
3. `dice_roles.py` - rolls 2 6-sided dice.
    - Inspired by randomness and craps, I asked chatGPT to "write a python program that simulates the role of two six-sided dice and generates a histogram of results." 
    - I probably could have written it myself, but it was easier to ask chatGPT to do it, and it worked!
4. `wiki_articles.py` - displays the 10 most recently-updated articles.
    - I asked chatGPT if wikipedia had an API, then to write a program that would display the 10 most recently-updated articles.
    - "Create a python program that appends the titles of the most recently edited Wikipedia articles to a text file."
    - I thought I wasn't getting any responses, but it was because I had the output file open in VSCode, and it doesn't update text files in real time, I have to close & open the file again to see changes.
5. `your_youtube.py` - displays the 10 most recently-added YouTube videos.
    - I decided to switch to the YouTube API, which necessitated signing up with the Google develper program to get an API key. I didn't really try this sample until after I got the search location working.
6. `youtube_search_loc.py` - displays the 10 most recently-added YouTube videos in a specific location.
    - I skipped to this as I wanted to see the 10 most recent YouTube videos in a particular location. I had some trouble getting this running. See the section below for details.
7. `lat_long.py` - Displays the latitude and longitude for an address. Uses the Google Maps API.
    - I needed the latitude and longitude for the YouTube search location so I asked chatGPT to help me with the maps API.
    - This API required a separate API Key so I got that and ran it successfully.
8. `yt_loc2.py` - User-friendly YouTube search by location.
    - This integrates the YouTube search app with the latitude and longitude app and adds input questions in the console for an easier experience.
9. `gnews_scraper.py` - Scrape Google News headlines.
    - Just grabs the top stories. Can't figure out how to get all the stories on the page yet.
    - **Updated to pull latest 5 headlines based on `h4` top stories.**
10. `gensen_worddict.py` - Expanded `random_sentence.py`.
    - Pulls random words from the `https://random-word-api.herokuapp.com/word` API endpoint and strings them together to create a sentence, then verifies the sentence against the `language_tool_python` API.
    - **TODO:** Needs articles added to create a valid sentence.
11. `gen_pass.py` - Generate passphrase.
    - Uses the `https://random-word-api.herokuapp.com/word` API endpoint to generate a passphrase.
    - As it is, this creates very complex passphrases that may be easier to remember than random character strings, but they're very long and complex.
    - **TODO:** Needs to use simpler words that can be easily remembered, less capitalization (however this may make them less secure).
12. `news_scraper` - BBC and NY Times headline scraper.
    - Adapted [Indently's BBC News Headline scraper](https://www.youtube.com/watch?v=zo7yzIVpIJo) to scrape BBC news and New York Times headlines.
    - Removed keyword highlighter.
13. `dlvideo.py` - Download YouTube, TikTok, and other videos from URL using `yt_dlp`.
14. `ytdlchatvidthreads.py` - Download YouTube Live video and chat.
15. `readmultijson.py` - Extract message and username from YouTube Live chat JSON file.

## YouTube search

* I had to educate myself about how to get an API key. The Google console is excessively complex, but I was able to add the YouTube endpoint and restrict the API key to that API. I did the same for the Google Maps API key later.
* chatGPT omitted the location radius value, which is required if you pass location. I figured this out by reading the YouTube endpoint doc.
* I was getting some errors. I discovered it had to do with the location parameter by doing some experimentation with the URL. Removing the `location` query parameter worked, so I figured it had something to do with that.

### Latitude and longitude

* Was using the wrong longitude. I didn't realize I needed to use a negative number for the longitude until I realized I was getting responses from a country in the eastern part of the globe instead of New York.
* I found the correct longitude on Google Maps, so I thought I could use the API to make this simpler.
* I got errors and narrowed it down to the radius. I forgot that the radius needed a measurement value, like `mi` for miles. And my input request left it out, so I fixed this.

## Programming notes & links

* I don't know why I get this error in the console when I run `dice_roles.py`, But I think it's something I can ignore. [1](https://stackoverflow.com/questions/7196197/catransaction-synchronize-called-within-transaction) [2](https://github.com/spyder-ide/spyder/issues/20444)
  ```
  +[CATransaction synchronize] called within transaction
  ```
* [Pyplot tutorial](https://matplotlib.org/stable/tutorials/introductory/pyplot.html) - something to read later.
* Had some trouble setting the environment variable using the `.env` file. [3](https://stackoverflow.com/questions/40728259/updated-environment-variable-but-os-getenv-keeps-returning-none) [4](https://www.php.net/manual/en/function.getenv.php) [5](https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5) [6](https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs) 
  * I had this issue before and solved it with `load_dotenv()`. [7](https://pypi.org/project/python-dotenv/) 
    * But I still can't figure out why `os.getenv`  doesn't just work.
* [The twelve-factor app](https://12factor.net/) - mentioned in the [python-dotenv](https://pypi.org/project/python-dotenv/) doc. It's a methodology for building Software as a service (SaaS) apps.
* [Format JSON in VSCode](https://code.visualstudio.com/docs/editor/codebasics#_formatting) - I got some JSON errors back and wanted to read it better so I wanted to know how to format JSON in VSCode. 
  * This ended up not working for the initial error as it wasn't properly formatted, so I had to do it manually, but subsequent JSON was properly formatted and this did help. 
  * Basically, used the Command Palette (⇧⌘P) and chose Format Selection. 
* [requests](https://pypi.org/project/requests/) - doc for the python HTTP requests library, which makes it easy to send requests in python.
* [MediaWiki API help](https://en.wikipedia.org/w/api.php).
* [Jump Start Solution guides](https://cloud.google.com/architecture/all-jss-guides) - "Cloud Architecture Center - Discover reference architectures, guidance, and best practices for building or migrating your workloads on Google Cloud."
* I included `pip>=23.0.1` in my requirements.txt file as I kept getting a note that I had an earlier version. But I still get the note, even when I add this.
* Run `pip list` to [list installed packages](packages.txt).
* [Is there a command to undo git?](https://stackoverflow.com/questions/3212459/is-there-a-command-to-undo-git-init) <br /> `rm -rf .git`
* [Adding locally hosted code to github](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
* [Is there a better guide to using yt-dlp with Python?](https://www.reddit.com/r/youtubedl/comments/skgjon/is_there_a_better_guide_to_using_ytdlp_with_python/) [comment](https://www.reddit.com/r/youtubedl/comments/skgjon/comment/hvl1xcg/?utm_source=reddit&utm_medium=web2x&context=3) lists locations of [`YoutubeDL` class](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L191) and [YT-DLP CLI](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) usage.

### Git asks for SSH key & passphrase

[Git keeps asking me for my SSH key and passphrase](https://stackoverflow.com/questions/10032461/git-keeps-asking-me-for-my-ssh-key-passphrase)

<blockquote>
<p>I created keys as instructed in the github tutorial, registered them with github, and tried using ssh-agent explicitly — yet git continues to ask me for my passphrase every time I try to do a pull or a push.</p>

<p>What could be the cause?</p>

---

Once you have started the SSH agent with:

`eval $(ssh-agent)`

Do either:

To add your private key to it:

`ssh-add`

This will ask you your passphrase just once, and then you should be allowed to push, provided that you uploaded the public key to Github.
To add and save your key permanently on macOS:

`ssh-add -K`

This will persist it after you close and re-open it by storing it in user's keychain.

If you see a warning about deprecated flags, try the new variant:

`ssh-add --apple-use-keychain`

To add and save your key permanently on Ubuntu (or equivalent):

  `ssh-add ~/.ssh/id_rsa`
</blockquote>

### YouTube & Google APIs

* [Youtube Python API samples](https://github.com/youtube/api-samples/blob/master/python/geolocation_search.py)
* [YouTube Analytics API](https://console.cloud.google.com/marketplace/product/google/youtubeanalytics.googleapis.com) - **not** the one I needed.
* [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started) - this is the API I used for search; v3.
* [Obtaining authorization credentials (Youtube API)](https://developers.google.com/youtube/registering_an_application)
* [YouTube Data API v3](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
* [Youtube search API](https://developers.google.com/youtube/v3/docs/search) - this didn't tell me what I needed to know about the location parameter.
* [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list) - this didn't help either.
* [Search:list location](https://developers.google.com/youtube/v3/docs/search/list#location) - Helped with `yt_loc2.py` error. It said I needed to add the `locationRadius` as well.
* [Let users watch, find, and manage YouTube content (main API page)](https://developers.google.com/youtube) - I kept getting this page, which is not useful as I can't get anywhere from here.
* [Request contains an invalid argument Location paramter \[sic\] Youtube API ](https://stackoverflow.com/questions/72883738/request-contains-an-invalid-argument-location-paramter-youtube-api) - This helped me troubleshoot errors I was having with sending an invalid location parameter. Prior to this, I didn't know how to specify the latitude and longitude. I had been sending it as `(lat,long)` with the parentheses, but this answer showed that I should not use that.
* [Address Geocoding in the Google Maps APIs](https://cloud.google.com/blog/products/maps-platform/address-geocoding-in-google-maps-apis)
* [Maps API metrics](https://console.cloud.google.com/google/maps-apis/metrics)
* [Google console API dashboard](https://console.cloud.google.com/apis/dashboard)
* [Google console credentials page](https://console.cloud.google.com/apis/credentials)
* [billing change not allowed](https://support.google.com/paymentscenter/answer/9791006) - I had an issue using PayPal. Don't know why.

### Links
* Random word & dictionary APIs
  * https://developer.wordnik.com/docs#!/words/getRandomWord
  * https://random-word-api.herokuapp.com/home
  * https://pipedream.com/apps/dictionary-api
    * https://dictionaryapi.dev/
    * https://pipedream.com/apps/dictionary-api/integrations/google
  * https://rapidapi.com/blog/dictionary-apis/
  * https://www.wordsapi.com/
    * https://www.wordsapi.com/docs/#random-words
  * https://www.reddit.com/r/learnprogramming/comments/uslfi2/looking_for_a_random_word_api_where_i_can_specify/
    * https://github.com/nltk/nltk
    * https://www.datamuse.com/api/
* https://pypi.org/project/language-tool-python/
  * https://languagetool.org/
* https://docs.python.org/3/library/unittest.html
* https://stackabuse.com/guide-to-parsing-html-with-beautifulsoup-in-python/
* https://www.geeksforgeeks.org/beautifulsoup-scraping-paragraphs-from-html/
* https://towardsdatascience.com/web-scraping-basics-82f8b5acd45c

## Additional resources

* [chatGPT documentation](chatGPT%20documentation.md)
* [Claude debugging](Claude%20debugging.md)
* [TODO](TODO.md)
* [packages](packages.txt)

## stash
*Google search notes*

```
On Dec 5, Code Tips will be merged with SGE. Please enable SGE to continue receiving coding responses.
git stash
Git stash is a command that saves the current state of your working directory and index in a temporary stash area. This can be useful if you want to save your work in progress and switch to another branch, or if you want to experiment with some changes without affecting your current working directory.

To use git stash, simply run the following command:

git stash

This will save the current state of your working directory and index in a temporary stash area. You can then switch to another branch or experiment with some changes. To restore the changes from the stash, run the following command:

git stash pop

This will restore the changes from the most recent stash. If you want to restore a specific stash, you can use the following command:

git stash apply <stash_id>

where <stash_id> is the ID of the stash you want to apply.
```
* [SGE](https://labs.google/sge/)