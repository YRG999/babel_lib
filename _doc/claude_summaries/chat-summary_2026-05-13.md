# Session Summary – 2026-05-13

## Troubleshooting YouTube Transcript Downloads

**Problem:** `--transcript-only` flag was not downloading transcripts from YouTube videos, even though transcripts were visible on the website.

**Root Cause:** yt-dlp was looking only for `en` subtitles, but many YouTube videos return subtitles with locale-specific codes like `en-US`, `en-GB`, etc. The fix involved discovering that the target video had `en-US` captions available.

**Solution:** Updated [youtube-downloader-app/src/downloader.py](youtube-downloader-app/src/downloader.py) to try multiple English subtitle variants (`en`, `en-US`, `en-GB`, `en-AU`) across all three download modes:
- `--transcript-only`
- `--metadata-only`
- Full video download

**Files Updated:**
- `youtube-downloader-app/src/downloader.py` — added subtitle language variants
- `youtube-downloader-app/CLAUDE.md` — documented the English subtitle behavior
- `CHANGELOG.md` — created with entry for the fix

**Diagnostic Commands Used:**
```bash
# Showed no en subtitles initially
yt-dlp --write-subs --write-auto-subs --sub-langs en --skip-download "URL"

# Revealed en-US was available
yt-dlp --list-subs "URL"
```

