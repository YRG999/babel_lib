# infojson2csv

Converts yt-dlp `.info.json` files to a single CSV, one row per video. Optionally writes a Markdown file with title, URL, and description for each video.

## Usage

```bash
python ytdownload/infojson2csv.py [DIRECTORY] [-o OUTPUT.csv] [--no-markdown]
```

| Argument | Default | Description |
| --- | --- | --- |
| `DIRECTORY` | `.` (current dir) | Root directory to search recursively |
| `-o` / `--output` | `<DIRECTORY>/infojson_output_<datetime_EST>.csv` | Output CSV file path |
| `--markdown` / `--no-markdown` | on | Also write a Markdown file alongside the CSV |

### Examples

```bash
# Search videos/, write CSV and Markdown to videos/ with EST timestamp
python ytdownload/infojson2csv.py videos/

# Custom output path, no Markdown
python ytdownload/infojson2csv.py videos/ -o videos.csv --no-markdown

# Search current directory with default output name
python ytdownload/infojson2csv.py
```

## Output Files

### CSV

One row per `.info.json` file found. Files that fail to parse are skipped with a warning.

Default filename: `infojson_output_YYYYMMDD_HHMMSS.csv` (EST timestamp, written to the search directory).

### Markdown (default on)

Same base name as the CSV with a `.md` extension. Contains one entry per video:

```markdown
# Video Title

**URL:** https://www.youtube.com/watch?v=...

Description text here...

---
```

Disable with `--no-markdown`.

## CSV Columns

| Column | Source field | Notes |
| --- | --- | --- |
| `file_path` | _(derived)_ | Path relative to search root |
| `id` | `id` | YouTube video ID |
| `title` | `title` | |
| `channel` | `channel` | |
| `channel_id` | `channel_id` | |
| `channel_url` | `channel_url` | |
| `uploader` | `uploader` | |
| `uploader_id` | `uploader_id` | e.g. `@handle` |
| `uploader_url` | `uploader_url` | |
| `upload_date` | `upload_date` | Format: `YYYYMMDD` |
| `duration` | `duration` | Seconds |
| `duration_string` | `duration_string` | e.g. `1:23:45` |
| `view_count` | `view_count` | |
| `like_count` | `like_count` | |
| `comment_count` | `comment_count` | |
| `channel_follower_count` | `channel_follower_count` | |
| `webpage_url` | `webpage_url` | Full YouTube URL |
| `thumbnail` | `thumbnail` | URL of highest-res thumbnail |
| `age_limit` | `age_limit` | |
| `availability` | `availability` | e.g. `public`, `unlisted` |
| `live_status` | `live_status` | e.g. `not_live`, `was_live` |
| `media_type` | `media_type` | e.g. `video`, `livestream` |
| `width` | `width` | Pixels |
| `height` | `height` | Pixels |
| `fps` | `fps` | |
| `resolution` | `resolution` | e.g. `1920x1080` |
| `ext` | `ext` | e.g. `mp4`, `webm` |
| `filesize_approx` | `filesize_approx` | Bytes |
| `description` | `description` | Full video description |
| `categories` | `categories` | List joined with "; " |
| `tags` | `tags` | List joined with "; " |

### Example CSV output

```csv
file_path,id,title,channel,upload_date,duration_string,view_count,...
singletons/20260220 feralhistorian American Gods/American Gods ...,EPZh_3RpKbw,American Gods : Land and Egregores,Feral Historian,20260220,18:02,18192,...
```

## Related Documentation

- [README.md](README.md) - ytdownload toolkit overview
- [CHANGELOG_infojson2csv.md](CHANGELOG_infojson2csv.md) - version history
