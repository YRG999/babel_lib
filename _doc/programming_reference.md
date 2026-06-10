# Programming reference

*Thematic reference — add entries here for reference tables, API links, how-to notes, and conceptual explanations organized by topic. For dated problem/fix entries, use [programming_notes.md](programming_notes.md).*

- [Experiments - more details](#experiments---more-details)
- [YouTube \& yt-dlp](#youtube--yt-dlp)
- [Git](#git)
- [Programming notes \& links](#programming-notes--links)
- [Python \& pip](#python--pip)
- [Claude Code](#claude-code)
- [Reference](#reference)

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

## YouTube & yt-dlp

### YouTube search

- I had to educate myself about how to get an API key. The Google console is excessively complex, but I was able to add the YouTube endpoint and restrict the API key to that API. I did the same for the Google Maps API key later.
- chatGPT omitted the location radius value, which is required if you pass location. I figured this out by reading the YouTube endpoint doc.
- I was getting some errors. I discovered it had to do with the location parameter by doing some experimentation with the URL. Removing the `location` query parameter worked, so I figured it had something to do with that.

### Latitude and longitude

- Was using the wrong longitude. I didn't realize I needed to use a negative number for the longitude until I realized I was getting responses from a country in the eastern part of the globe instead of New York.
- I found the correct longitude on Google Maps, so I thought I could use the API to make this simpler.
- I got errors and narrowed it down to the radius. I forgot that the radius needed a measurement value, like `mi` for miles. And my input request left it out, so I fixed this.

### YouTube & Google APIs

- [Youtube Python API samples](https://github.com/youtube/api-samples/blob/master/python/geolocation_search.py)
- [YouTube Analytics API](https://console.cloud.google.com/marketplace/product/google/youtubeanalytics.googleapis.com) - **not** the one I needed.
- [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started) - this is the API I used for search; v3.
- [Obtaining authorization credentials (Youtube API)](https://developers.google.com/youtube/registering_an_application)
- [YouTube Data API v3](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
- [Youtube search API](https://developers.google.com/youtube/v3/docs/search) - this didn't tell me what I needed to know about the location parameter.
- [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list) - this didn't help either.
- [Search:list location](https://developers.google.com/youtube/v3/docs/search/list#location) - Helped with `yt_loc2.py` error. It said I needed to add the `locationRadius` as well.
- [Let users watch, find, and manage YouTube content (main API page)](https://developers.google.com/youtube) - I kept getting this page, which is not useful as I can't get anywhere from here.
- [Request contains an invalid argument Location paramter \[sic\] Youtube API](https://stackoverflow.com/questions/72883738/request-contains-an-invalid-argument-location-paramter-youtube-api) - This helped me troubleshoot errors I was having with sending an invalid location parameter. Prior to this, I didn't know how to specify the latitude and longitude. I had been sending it as `(lat,long)` with the parentheses, but this answer showed that I should not use that.
- [Address Geocoding in the Google Maps APIs](https://cloud.google.com/blog/products/maps-platform/address-geocoding-in-google-maps-apis)
- [Maps API metrics](https://console.cloud.google.com/google/maps-apis/metrics)
- [Google console API dashboard](https://console.cloud.google.com/apis/dashboard)
- [Google console credentials page](https://console.cloud.google.com/apis/credentials)
- [billing change not allowed](https://support.google.com/paymentscenter/answer/9791006) - I had an issue using PayPal. Don't know why.

### yt-dlp tips

```zsh
# Download best quality video+audio, merge to mp4
# This one worked when webm was downloading & failing to merge
yt-dlp -f "bv*+ba/b" --merge-output-format mp4 URL

# Or download best video+audio up to 1080p
yt-dlp -f "bv*[height<=1080]+ba/b" URL

# Prefer mp4 video codec (more compatible)
yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" URL
```

### Downloading live videos

Always quote the URL in zsh — `?` is a glob wildcard and will cause "no matches found" without quotes.

- <https://superuser.com/questions/649635/zsh-says-no-matches-found-when-trying-to-download-video-with-youtube-dl>
- `yt-dlp 'https://www.youtube.com/watch?v=####'`

## Git

### SSH key & passphrase

[Git keeps asking me for my SSH key and passphrase](https://stackoverflow.com/questions/10032461/git-keeps-asking-me-for-my-ssh-key-passphrase)

> I created keys as instructed in the github tutorial, registered them with github, and tried using ssh-agent explicitly — yet git continues to ask me for my passphrase every time I try to do a pull or a push.
>
> What could be the cause?
>
> ---
>
> Once you have started the SSH agent with:
>
> `eval $(ssh-agent)`
>
> Do either:
>
> To add your private key to it:
>
> `ssh-add`
>
> This will ask you your passphrase just once, and then you should be allowed to push, provided that you uploaded the public key to Github.
> To add and save your key permanently on macOS:
>
> `ssh-add -K`
>
> This will persist it after you close and re-open it by storing it in user's keychain.
>
> If you see a warning about deprecated flags, try the new variant:
>
> `ssh-add --apple-use-keychain`
>
> To add and save your key permanently on Ubuntu (or equivalent):
>
> `ssh-add ~/.ssh/id_rsa`

### Git stash

Git stash is a command that saves the current state of your working directory and index in a temporary stash area. This can be useful if you want to save your work in progress and switch to another branch, or if you want to experiment with some changes without affecting your current working directory.

To use git stash, simply run the following command:

```zsh
git stash
```

This will save the current state of your working directory and index in a temporary stash area. You can then switch to another branch or experiment with some changes. To restore the changes from the stash, run the following command:

```zsh
git stash pop
```

This will restore the changes from the most recent stash. If you want to restore a specific stash, you can use the following command:

```zsh
git stash apply <stash_id>
```

where `<stash_id>` is the ID of the stash you want to apply.

Source: *Google search*

## Programming notes & links

- I don't know why I get this error in the console when I run `dice_roles.py`, But I think it's something I can ignore. [1](https://stackoverflow.com/questions/7196197/catransaction-synchronize-called-within-transaction) [2](https://github.com/spyder-ide/spyder/issues/20444)

  ```text
  +[CATransaction synchronize] called within transaction
  ```

- [Pyplot tutorial](https://matplotlib.org/stable/tutorials/introductory/pyplot.html) - something to read later.
- Had some trouble setting the environment variable using the `.env` file. [3](https://stackoverflow.com/questions/40728259/updated-environment-variable-but-os-getenv-keeps-returning-none) [4](https://www.php.net/manual/en/function.getenv.php) [5](https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5) [6](https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs)
  - I had this issue before and solved it with `load_dotenv()`. [7](https://pypi.org/project/python-dotenv/)
    - But I still can't figure out why `os.getenv` doesn't just work.
- [The twelve-factor app](https://12factor.net/) - mentioned in the [python-dotenv](https://pypi.org/project/python-dotenv/) doc. It's a methodology for building Software as a service (SaaS) apps.
- [Format JSON in VSCode](https://code.visualstudio.com/docs/editor/codebasics#_formatting) - I got some JSON errors back and wanted to read it better so I wanted to know how to format JSON in VSCode.
  - This ended up not working for the initial error as it wasn't properly formatted, so I had to do it manually, but subsequent JSON was properly formatted and this did help.
  - Basically, used the Command Palette (⇧⌘P) and chose Format Selection.
- [requests](https://pypi.org/project/requests/) - doc for the python HTTP requests library, which makes it easy to send requests in python.
- [MediaWiki API help](https://en.wikipedia.org/w/api.php).
- [Jump Start Solution guides](https://cloud.google.com/architecture/all-jss-guides) - "Cloud Architecture Center - Discover reference architectures, guidance, and best practices for building or migrating your workloads on Google Cloud."
- I included `pip>=23.0.1` in my requirements.txt file as I kept getting a note that I had an earlier version. But I still get the note, even when I add this.
- Run `pip list` to [list installed packages](packages.txt).
- [Is there a command to undo git?](https://stackoverflow.com/questions/3212459/is-there-a-command-to-undo-git-init) `rm -rf .git`
- [Adding locally hosted code to github](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Is there a better guide to using yt-dlp with Python?](https://www.reddit.com/r/youtubedl/comments/skgjon/is_there_a_better_guide_to_using_ytdlp_with_python/) [comment](https://www.reddit.com/r/youtubedl/comments/skgjon/comment/hvl1xcg/?utm_source=reddit&utm_medium=web2x&context=3) lists locations of [`YoutubeDL` class](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L191) and [YT-DLP CLI](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp) usage.

## Python & pip

### pip upgrading packages

- Instructions from: <https://www.activestate.com/resources/quick-reads/how-to-update-all-python-packages/>
- In a requirements file, "unpinned packages are typically denoted by >=, which indicates that the package can be replaced by a later version."
- get list of outdated packages: `pip list --outdated`
- output packages `pip freeze > requirements.txt`
- Edit requirements.txt, and replace all '==' with '>='.
- Upgrade outdated packages: `pip install -r requirements.txt --upgrade`

### Testing APIs

- [rapidapi.com](https://rapidapi.com/hub)
- [api-ninjas.com](https://api-ninjas.com/)

## Security concepts (from the 2026-06-10 youtube-downloader-app fixes)

Plain-language explanations of the security issues fixed in `youtube-downloader-app` on 2026-06-10 (CHANGELOG version 2.3.0). Each entry explains the underlying concept, why it matters, and what the fix was.

### TLS certificate verification (`nocheckcertificate`)

When a program connects to a website over HTTPS, two things happen: the traffic is **encrypted**, and the server proves its identity with a **certificate** — a digital document, signed by a trusted authority, that says "this server really is youtube.com." Your program checks that signature before sending anything.

`downloader.py` had the option `'nocheckcertificate': True`, which tells yt-dlp to skip that identity check. The connection is still encrypted, but you no longer know *who* you're encrypting to. Anyone positioned between you and YouTube — say, the operator of a coffee-shop Wi-Fi network — could present their own fake certificate, and the program would happily talk to them instead. This is called a **man-in-the-middle (MITM) attack**: the attacker relays traffic in both directions, reading or modifying it as it passes through. For a downloader, that means the video, subtitles, or even yt-dlp's responses could be tampered with in transit.

People usually add this option to silence a one-time certificate error and then forget about it. There was no documented reason for it here, so the fix was simply to delete the line — verification is on by default.

### Remote code components (`ejs:npm` → `ejs:github`)

YouTube makes scrapers solve small JavaScript puzzles before serving videos. yt-dlp handles this by downloading a solver component from the internet and **executing it** — which means you are running code written by someone else, fetched at runtime. That's inherently a matter of trust: if the place you fetch it from is compromised, you run the attacker's code.

This is an example of **supply-chain risk** — being attacked not directly, but through something you depend on. The option was set to fetch the solver from `npm` (the JavaScript package registry, where anyone can publish and account takeovers have happened repeatedly). yt-dlp's own warning message recommends `ejs:github`, which fetches from yt-dlp's own GitHub releases — the same people whose code you're already trusting by running yt-dlp at all. The fix doesn't eliminate the risk (remote code is still fetched and run); it narrows who you have to trust to a party you already trust.

### Don't print secrets to the terminal (cookie redaction)

`kick_live_downloader.py` printed the full ffmpeg command before running it — useful for debugging. The problem: that command included a `Cookie:` header containing your live Kick **session cookies**.

A session cookie is the small token a website gives your browser after you log in; presenting it *is* being logged in. Anyone who copies that string can act as you on that site without knowing your password. Terminal output isn't private: it lingers in scrollback, gets saved when you copy output into notes or a bug report, and may be written to log files. The classic mistake is pasting a "harmless" debug log somewhere public with a token buried in the middle of it.

The fix keeps the helpful debug printout but replaces the headers value with `<redacted>`. Rule of thumb: log *that* you sent credentials, never *what* they were.

### File permissions (`0600` on cookies.txt)

Unix-family systems (macOS included) attach three sets of permissions to every file: what the **owner** can do, what the file's **group** can do, and what **everyone else** can do. Each set is read/write/execute, written as an octal number. `0600` means: owner can read and write (`6`), group gets nothing (`0`), others get nothing (`0`). In `ls -l` that shows as `-rw-------`.

By default, files you create are often readable by other accounts on the machine (`0644`, `-rw-r--r--`). For most files that's fine. But `firefox_cookie_export.py` writes your browser session cookies — credentials, per the section above — into a plain text file. Any other process or user account that can read the file can hijack your sessions.

The fix creates the file with restrictive permissions from the start:

```python
fd = os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with open(fd, "w", encoding="utf-8") as f:
    ...
```

The lower-level `os.open` is used instead of plain `open()` because it accepts a permission mode at creation time. That matters: setting permissions *after* writing (e.g., with `os.chmod`) leaves a brief window where the file exists with loose permissions and sensitive content already in it.

### Argument injection (`--` before the URL)

The downloader runs yt-dlp as a subprocess, passing the URL as a command-line argument:

```python
subprocess.run(["yt-dlp", "-o", out_pattern, url])
```

Command-line programs can't tell options from data by position alone — they just see a list of strings, and anything starting with `-` is treated as an option. So if the "URL" were the string `--exec=rm -rf ~`, yt-dlp would not say "that's not a URL"; it would recognize its own `--exec` option, which runs an arbitrary shell command after downloading. The data slot has been used to inject an instruction. (This is the command-line cousin of SQL injection from 6.0001-era lore: data crossing over into being interpreted as code.)

The fix is the standard Unix convention `--`, a separator meaning "everything after this is data, even if it starts with a dash":

```python
subprocess.run(["yt-dlp", "-o", out_pattern, "--", url])
```

Note this is a *defense-in-depth* fix — today the URL comes from you typing it, not from an attacker. But scripts get reused, wrapped, and fed input from files or other programs, and the guard costs two characters.

### Pinned dependencies and missing requirements

`requirements.txt` listed bare package names (`yt-dlp`, `requests`, ...) with no versions. That means `pip install -r requirements.txt` grabs whatever the latest version is *on the day you run it* — so two installs months apart can behave differently, and if a package release is ever compromised (see supply-chain risk above), you'd pull it in automatically with no record of what you'd been running before.

Minimum-version pins (`requests>=2.31.0`) are a light-touch middle ground: they document what the code was developed against and refuse anything older (older versions may contain known, since-fixed vulnerabilities), while still allowing updates. The file was also missing `playwright` entirely — the Kick live fallback imports it, so a fresh install of the requirements file would crash at runtime with `ModuleNotFoundError`. It's now listed, with a reminder that Playwright also needs a post-install step (`playwright install firefox`) to download the browser itself.

### CSV / formula injection (documented, deliberately not fixed)

Spreadsheet programs treat a cell that begins with `=` (and sometimes `+`, `-`, or `@`) as a **formula**, not text — and this applies even to plain `.csv` files. Old Excel formula families like `=DDE(...)` could launch external programs. Now consider that the chat CSVs in this project contain messages typed by *arbitrary strangers on the internet*. A malicious viewer only has to type a message starting with `=` and wait for someone to open the downloaded chat log in Excel. The file itself is harmless; the spreadsheet app is what executes it. This is the same lesson as argument injection: untrusted data ending up somewhere it gets *interpreted*.

The standard fix is to prefix risky cells with `'` or a space, but that alters the message text, and these CSVs exist for chat analysis where exact text matters. So the decision (recorded in the README, "Opening chat CSVs safely") was to leave the data verbatim and handle the files safely instead: open them in a text editor or pandas, or use a spreadsheet's *import as text* path rather than double-clicking the file.

## Claude Code

### Saving chat output to a file

There is no built-in command to export an interactive Claude Code chat session. Options:

- **Interactive sessions:** Sessions are automatically persisted locally. Resume with `claude --continue` (last session) or `claude --resume`. Copy/paste or use your terminal's scrollback save for ad-hoc export.
- **Non-interactive (`-p` flag):** Supports piping and output format flags:

```zsh
# Plain text output
claude -p "your prompt" > output.txt

# Full JSON (includes cost, duration, metadata)
claude -p "your prompt" --output-format json > output.json

# Streaming JSON (real-time, one event per line)
claude -p "your prompt" --output-format stream-json > output.jsonl

# Pipe a file through Claude and save the result
cat file.txt | claude -p "summarize this" > summary.txt
```

### Checking and updating Claude Code version

Check your current version:

```zsh
claude --version
```

Check the latest version available on npm:

```zsh
npm view @anthropic-ai/claude-code version
```

Compare both at once:

```zsh
claude --version && npm view @anthropic-ai/claude-code version
```

Latest releases and changelog: <https://github.com/anthropics/claude-code/releases>

**Update behavior by installation method:**

| Method | Auto-updates? | Update command |
| --- | --- | --- |
| Native install (curl script) | Yes, background | `claude update` |
| Desktop app | Yes, automatic | — |
| VS Code extension | Yes, via marketplace | Extensions view → Update |
| Homebrew | No | `brew upgrade claude-code` |
| WinGet | No | `winget upgrade Anthropic.ClaudeCode` |

**Note:** The VS Code extension and the terminal CLI are separate installations with independent versions. If both are installed, update them separately.

**Find all CLI installations:**

```zsh
which -a claude
```

**Uninstall CLI (if using VS Code extension only):**

```zsh
# npm install
npm uninstall -g @anthropic-ai/claude-code

# Homebrew install
brew uninstall claude-code

# Native install (curl script) — binary is at ~/.local/bin/claude
rm ~/.local/bin/claude
```

**Update channel (native install only):** Controls whether you get updates immediately or ~1 week delayed. Configure in `~/.claude/settings.json` or via `/config`:

```json
{ "autoUpdatesChannel": "stable" }
```

Options: `"latest"` (default, immediate) or `"stable"` (~1 week delayed, skips bad releases).

### Session log files

Session logs are stored as `.jsonl` files (newline-delimited JSON, one event per line):

- **Global history:** `~/.claude/history.jsonl`
- **Per-project sessions:** `~/.claude/projects/<encoded-project-path>/<session-id>.jsonl`
- **Other data:** `~/.claude/` also contains `stats-cache.json`, `todos`, `settings.json`, `cache/`, etc.

The project path is encoded by replacing `/` with `-` (e.g. `/Users/name/Repos/myproject` → `-Users-name-Repos-myproject`).

```zsh
# List sessions for the current project (most recent first)
ls -lt ~/.claude/projects/<encoded-project-path>/*.jsonl | head

# Read a specific session
cat ~/.claude/projects/<encoded-project-path>/<session-id>.jsonl
```

## Reference

### Links

- MIT intro Python courses (good resources for learning Python, though the original pair dates from 2016 and may be out of date)
  - <https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/> - 6.0001: MIT's introduction to programming in Python — variables, functions, recursion, data structures, classes, and algorithmic thinking, with full lecture videos and assignments.
  - <https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/> - 6.0002: the follow-on course covering optimization, simulation, randomness, statistics, and machine-learning basics in Python.
  - Updated versions (as of 2026 — MIT renumbered these courses in 2022; 6.0001 became 6.100A/6.100L and 6.0002 became 6.100B):
    - <https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/> - 6.100L (Fall 2022): the modernized full-semester version of 6.0001 on OCW, with newer lectures by Ana Bell.
    - <https://www.edx.org/learn/computer-science/massachusetts-institute-of-technology-introduction-to-computer-science-and-programming-using-python> - MITx 6.00.1x on edX: the actively maintained, instructor-paced online version of the intro course with graded exercises.
    - <https://www.edx.org/learn/computer-science/massachusetts-institute-of-technology-introduction-to-computational-thinking-and-data-science> - MITx 6.00.2x on edX: the actively maintained online version of the computational thinking / data science follow-on.
- Random word & dictionary APIs
  - <https://developer.wordnik.com/docs#!/words/getRandomWord>
  - <https://random-word-api.herokuapp.com/home>
  - <https://pipedream.com/apps/dictionary-api>
    - <https://dictionaryapi.dev/>
    - <https://pipedream.com/apps/dictionary-api/integrations/google>
  - <https://rapidapi.com/blog/dictionary-apis/>
  - <https://www.wordsapi.com/>
    - <https://www.wordsapi.com/docs/#random-words>
  - <https://www.reddit.com/r/learnprogramming/comments/uslfi2/looking_for_a_random_word_api_where_i_can_specify/>
    - <https://github.com/nltk/nltk>
    - <https://www.datamuse.com/api/>
- <https://pypi.org/project/language-tool-python/>
  - <https://languagetool.org/>
- <https://docs.python.org/3/library/unittest.html>
- <https://stackabuse.com/guide-to-parsing-html-with-beautifulsoup-in-python/>
- <https://www.geeksforgeeks.org/beautifulsoup-scraping-paragraphs-from-html/>
- <https://towardsdatascience.com/web-scraping-basics-82f8b5acd45c>

### Additional resources

- [chatGPT documentation](chatGPT%20documentation.md)
- [Claude debugging](Claude%20debugging.md)
- [TODO](TODO.md)
- [packages](packages.txt)

### Markdown lint rules (markdownlint)

Common rules and fixes when using `markdownlint` / `markdownlint-cli2`:

| Rule | Description | Fix |
| --- | --- | --- |
| MD004 | Unordered list style inconsistent | Use `-` bullets throughout (not `*`) |
| MD009 | Trailing spaces | Remove single trailing spaces; 2 trailing spaces = intentional line break |
| MD022 | Headings not surrounded by blank lines | Add blank line before and after every heading |
| MD031 | Fenced code blocks not surrounded by blank lines | Add blank line before and after ` ``` ` fences |
| MD032 | Lists not surrounded by blank lines | Add blank line before and after list blocks |
| MD033 | Inline HTML | Replace `<br>`, `<blockquote>`, `<p>` etc. with native markdown |
| MD034 | Bare URLs | Wrap in `<>` (e.g. `<https://example.com>`) or use `[text](url)` |
| MD036 | Emphasis used instead of a heading | Change `*Section title*` to a proper `##` heading |
| MD039 | Spaces inside link text | Remove trailing space before `]` in `[link text ](url)` |
| MD040 | Fenced code block missing language | Add language after opening fence: ` ```text `, ` ```zsh `, etc. |
| MD047 | File must end with a single newline | Ensure one trailing newline at end of file |
| MD051 | Link fragment does not match any heading | Verify anchor `#heading-slug` matches an actual heading |
