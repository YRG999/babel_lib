# dir_compare.sh

A bash script that compares two directories and copies files from a source directory that don't exist in a destination directory.

## Usage

```bash
./dir_compare.sh <source_dir> <dest_dir> [--dry-run]
```

### Arguments

| Argument | Description |
| --- | --- |
| `source_dir` | The directory to copy files from |
| `dest_dir` | The directory to copy files into |
| `--dry-run` | (Optional) Preview what would be copied without making changes |

## Examples

Preview missing files with `--dry-run`:

```bash
bash dir_compare.sh "/Users/you/Photos/camera 2" "/Users/you/Photos/backup/" --dry-run
```

```text
Source:      /Users/you/Photos/camera 2
Destination: /Users/you/Photos/backup
Mode:        DRY RUN
-------------------------------------------
[would copy] 2024/march/IMG_001.jpg
[would copy] 2024/march/IMG_002.jpg
[would copy] notes.txt
-------------------------------------------
3 file(s) would be copied.
```

Copy the missing files:

```bash
bash dir_compare.sh "/Users/you/Photos/camera 2" "/Users/you/Photos/backup/"
```

```text
Source:      /Users/you/Photos/camera 2
Destination: /Users/you/Photos/backup
Mode:        COPY
-------------------------------------------
[copied] 2024/march/IMG_001.jpg
[copied] 2024/march/IMG_002.jpg
[copied] notes.txt
-------------------------------------------
3 file(s) copied.
```

## How it works

1. Recursively finds all files in the source directory
2. For each file, checks if the same relative path exists in the destination
3. If it doesn't exist, copies it (creating parent directories as needed)
4. Uses `cp -a` to preserve timestamps and permissions

## Notes

- Compares by file path, not by content — if a file exists at the same path in both directories it is skipped even if the contents differ
- Both directories must already exist
- Handles filenames with spaces and special characters
