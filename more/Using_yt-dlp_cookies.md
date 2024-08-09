# Using yt-dlp cookies

*From Claude 3.5 Sonnet.*

The yt-dlp --cookies-from-browser feature allows you to extract cookies from your web browser and use them with yt-dlp. This can be helpful for downloading content that requires authentication or for accessing region-restricted videos. Here's how to use this feature:

1. Basic syntax:

   ```zsh
   yt-dlp --cookies-from-browser BROWSER[:PROFILE_NAME[:KEYRING]] [URL]
   ```

2. Supported browsers:
   - chrome (Chromium)
   - chromium
   - firefox
   - opera
   - safari
   - edge

3. Examples:

   - For Chrome (default profile):

     ```zsh
     yt-dlp --cookies-from-browser chrome [URL]
     ```

   - For Firefox with a specific profile:

     ```zsh
     yt-dlp --cookies-from-browser firefox:profile_name [URL]
     ```

4. Additional options:
   - You can specify a keyring for password-protected browsers:

     ```zsh
     yt-dlp --cookies-from-browser firefox:profile_name:keyring [URL]
     ```

5. Notes:
   - Ensure your browser is closed when using this feature to avoid potential conflicts.
   - The browser must be installed in the default location for your operating system.
   - For some browsers, you may need to provide additional authentication or keyring information.

6. Troubleshooting:
   - If you encounter issues, try specifying the full path to your browser's cookie file directly using the `--cookies` option instead.

This feature can be particularly useful when downloading content from sites that require login or have region restrictions. It saves you the trouble of manually exporting cookies from your browser.

See also: <https://www.reddit.com/r/youtubedl/comments/15wn3mb/ytdlp_cant_download_from_twitter/>

## Find profile path

[To find your profile path in Chrome:](https://sessionbuddy.com/chrome-profile-location/), enter `chrome://version/` in the address bar.

## Download live from start with chat

```zsh
yt-dlp VIDEOSEGMENT --live-from-start --sub-langs live_chat
```

## Embedding yt-dlp

- See <https://github.com/yt-dlp/yt-dlp/blob/master/README.md#embedding-yt-dlp>
