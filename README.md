# BABEL_LIB

This is called BABEL_LIB after the [Library of Babel](https://libraryofbabel.info/) website.

It started as an experiment in randomness but now hosts a bunch of experimental programs.

I used chatGPT to help me write some of them.

## Experiments

*Listed in order of creation.*

1. `random_sentence.py` - creates random "words" and sentences.
    - In the spirit of the library of babel, I wanted to create a program that would string together random words to create sentences. 
    - Ideally I wanted to recreate the library of babel site so that I could create books and eventually find one that made sense. 
    - But with infinity, there's infinite nothingness and chaos as well as everything that's ever existed and ever will be, so I abandoned this. 
    - I also thought about adding a dictionary so that only words that made sense would be output, but abandoned that too.
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

## Requirements

* Sign up to develop with the [Google Cloud Platform](https://console.cloud.google.com/), create a project, and activate the YouTube Data API v3 and the Geocoding API.
* Create an `.env` file with `YOUTUBE_API_KEY=yourapikey` and `MAPS_API_KEY=yourmapsapikey`.

## YouTube search

* I had to educate myself about how to get an API key. The Google console is excessively complex, but I was able to add the YouTube endpoint and restrict the API key to that API. I did the same for the Google Maps API key later.
* chatGPT omitted the location radius value, which is required if you pass location. I figured this out by reading the YouTube endpoint doc (link to come).
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
* [MediaWiki API help](https://en.wikipedia.org/w/api.php) - didn't read it but here it is as a resource.
* [youtube python api samples](https://github.com/youtube/api-samples/blob/master/python/geolocation_search.py)
* [YouTube Analytics API](https://console.cloud.google.com/marketplace/product/google/youtubeanalytics.googleapis.com) - **not** the one I needed.
* [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started) - this is the API I used for search; v3.
* [Google console API dashboard](https://console.cloud.google.com/apis/dashboard)
* [Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application)
* [Google console credentials page](https://console.cloud.google.com/apis/credentials)
* [Address Geocoding in the Google Maps APIs](https://cloud.google.com/blog/products/maps-platform/address-geocoding-in-google-maps-apis)
* [maps api metrics](https://console.cloud.google.com/google/maps-apis/metrics)
* [billing change not allowed](https://support.google.com/paymentscenter/answer/9791006) - I had an issue using PayPal. Don't know why.
* [YouTube Data API v3](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
* [the youtube search API](https://developers.google.com/youtube/v3/docs/search) - this didn't tell me what I needed to know about the location parameter.
* [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list) - this didn't help either.
* [Search:list location](https://developers.google.com/youtube/v3/docs/search/list#location) - this helped. It said I needed to add the `locationRadius` as well.
* [Let users watch, find, and manage YouTube content (main API page)](https://developers.google.com/youtube) - I kept getting this page, which is not useful as I can't get anywhere from here.
* [Request contains an invalid argument Location paramter \[sic\] Youtube API ](https://stackoverflow.com/questions/72883738/request-contains-an-invalid-argument-location-paramter-youtube-api) - This helped me troubleshoot errors I was having with sending an invalid location parameter. Prior to this, I didn't know how to specify the latitude and longitude. I had been sending it as `(lat,long)` with the parentheses, but this answer showed that I should not use that.
* [Jump Start Solution: Log analysis pipeline](https://cloud.google.com/architecture/monitoring/log-analysis-pipeline) - this is totally off track and had nothing to do with anything. I just wanted to see what a jump start solution looked like, but I couldn't make sense of this (just a way to log and analyse data). Something for another day.
* Oh, I used a virtual environment and I keep forgetting how to set it up, so briefly, here's how:

```bash
$ python -m venv venv
$ . venv/bin/activate
```

* Then create a requirements file and manually add anything you install with `pip` to that file. I also included `pip>=23.0.1` as I kept getting a note that I had an earlier version.
* [Git keeps asking me for my ssh key passphrase](https://stackoverflow.com/questions/10032461/git-keeps-asking-me-for-my-ssh-key-passphrase) - helpful tip.