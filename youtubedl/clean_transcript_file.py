# Clean transcript file

from ytdl_updated import * 

def clean_transcript_file():
        file = input("Filename? ")
        clean_filename = clean_transcript(file)
        print(f"Transcript saved as: {clean_filename}")

if __name__ == "__main__":
    clean_transcript_file()