#!/bin/bash
# Compare two directories and copy files/folders from dir1 that don't exist in dir2.
# Usage: ./dir_compare.sh <dir1> <dir2> [--dry-run]

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <source_dir> <dest_dir> [--dry-run]"
    echo ""
    echo "Compares folders in source_dir vs dest_dir and copies over"
    echo "any files/folders that don't exist in dest_dir."
    echo ""
    echo "Options:"
    echo "  --dry-run   Show what would be copied without actually copying"
    exit 1
fi

DIR1="${1%/}"
DIR2="${2%/}"
DRY_RUN=false

if [[ "${3:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

if [[ ! -d "$DIR1" ]]; then
    echo "Error: source directory '$DIR1' does not exist."
    exit 1
fi

if [[ ! -d "$DIR2" ]]; then
    echo "Error: destination directory '$DIR2' does not exist."
    exit 1
fi

echo "Source:      $DIR1"
echo "Destination: $DIR2"
echo "Mode:        $( $DRY_RUN && echo 'DRY RUN' || echo 'COPY' )"
echo "-------------------------------------------"

count=0

# Find all files in dir1 relative to its root
while IFS= read -r -d '' rel_path; do
    if [[ ! -e "$DIR2/$rel_path" ]]; then
        count=$((count + 1))
        if $DRY_RUN; then
            echo "[would copy] $rel_path"
        else
            # Create parent directory if needed
            mkdir -p "$DIR2/$(dirname "$rel_path")"
            cp -a "$DIR1/$rel_path" "$DIR2/$rel_path"
            echo "[copied] $rel_path"
        fi
    fi
done < <(cd "$DIR1" && find . -type f -print0 | while IFS= read -r -d '' f; do printf '%s\0' "${f#./}"; done | sort -z)

echo "-------------------------------------------"
if $DRY_RUN; then
    echo "$count file(s) would be copied."
else
    echo "$count file(s) copied."
fi
