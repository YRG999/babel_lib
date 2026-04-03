#!/bin/bash
# Compare two directories and copy files/folders from dir1 that don't exist in dir2.
# Usage: ./dir_compare.sh <dir1> <dir2> [--dry-run]

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <source_dir> <dest_dir> [--dry-run | --compare]"
    echo ""
    echo "Compares folders in source_dir vs dest_dir and copies over"
    echo "any files/folders that don't exist in dest_dir."
    echo ""
    echo "Options:"
    echo "  --dry-run   Show what would be copied without actually copying"
    echo "  --compare   Show files missing from either directory and write results to a file"
    exit 1
fi

DIR1="${1%/}"
DIR2="${2%/}"
DRY_RUN=false
COMPARE=false

if [[ "${3:-}" == "--dry-run" ]]; then
    DRY_RUN=true
elif [[ "${3:-}" == "--compare" ]]; then
    COMPARE=true
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
echo "Mode:        $( $COMPARE && echo 'COMPARE' || ( $DRY_RUN && echo 'DRY RUN' || echo 'COPY' ) )"
echo "-------------------------------------------"

# Collect relative file paths from a directory (null-delimited, sorted)
list_files() {
    cd "$1" && find . -type f -print0 \
        | while IFS= read -r -d '' f; do printf '%s\0' "${f#./}"; done \
        | sort -z
}

compare_dirs() {
    local outfile="dir_compare_$(date +%Y%m%d_%H%M%S).txt"
    # Initialize output file
    > "$outfile"

    log() { echo "$*" | tee -a "$outfile"; }

    log "Directory comparison: $(date)"
    log "Dir1: $DIR1"
    log "Dir2: $DIR2"
    log "==========================================="

    local only_in_dir1=()
    while IFS= read -r -d '' rel_path; do
        [[ ! -e "$DIR2/$rel_path" ]] && only_in_dir1+=("$rel_path")
    done < <(list_files "$DIR1")

    local only_in_dir2=()
    while IFS= read -r -d '' rel_path; do
        [[ ! -e "$DIR1/$rel_path" ]] && only_in_dir2+=("$rel_path")
    done < <(list_files "$DIR2")

    log ""
    log "Files only in $DIR1 (${#only_in_dir1[@]}):"
    for f in "${only_in_dir1[@]+"${only_in_dir1[@]}"}"; do log "  $f"; done

    log ""
    log "Files only in $DIR2 (${#only_in_dir2[@]}):"
    for f in "${only_in_dir2[@]+"${only_in_dir2[@]}"}"; do log "  $f"; done

    log ""
    log "==========================================="
    log "Total missing from Dir2: ${#only_in_dir1[@]}  |  missing from Dir1: ${#only_in_dir2[@]}"
    echo ""
    echo "Results written to: $outfile"
}

if $COMPARE; then
    compare_dirs
    exit 0
fi

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
done < <(list_files "$DIR1")

echo "-------------------------------------------"
if $DRY_RUN; then
    echo "$count file(s) would be copied."
else
    echo "$count file(s) copied."
fi
