# merge_parts.py
# This script generates a filelist.txt for ffmpeg to merge .mp4.part files in the current directory.
# Usage: Run the script in the directory containing .mp4.part files.
# Make sure to have ffmpeg installed and available in your PATH.

import os

def create_filelist(directory: str, output_file: str = "filelist.txt"):
    # Find all .mp4.part files in the directory
    part_files = sorted([f for f in os.listdir(directory) if f.endswith(".mp4.part")])

    if not part_files:
        print("No .mp4.part files found in the directory.")
        return

    # Write the filelist.txt
    with open(output_file, "w") as filelist:
        for part_file in part_files:
            filelist.write(f"file '{part_file}'\n")

    print(f"Filelist created: {output_file}")
    print("\nRun the following command to merge the files:")
    print(f"\n\n\nffmpeg -f concat -safe 0 -i {output_file} -c copy output.mp4\n\n\n")

if __name__ == "__main__":
    current_directory = os.getcwd()
    create_filelist(current_directory)