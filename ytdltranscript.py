from youtube_functions import download_transcript, clean_transcript

# Download transcript
print("Enter video ID: ")
FULL_VIDEO_ID = input()
transcript_file = download_transcript(FULL_VIDEO_ID)
print(f"Transcript downloaded to: {transcript_file}")

# Clean transcript
cleaned_transcript = clean_transcript(transcript_file)
print(f"Cleaned transcript saved as: {cleaned_transcript}")