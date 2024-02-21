# Extract live comments from JSON & save to CSV
# First use ytdlchatvidthreads.py to download Youtube chat
# then use this to convert chat JSON to CSV
# Does the same thing as ytlivechatcsv.py

from youtube_functions import extract_data_from_json, write_to_csv

def ask_filename():
    print("Name or path of file to extract")
    filename = input()
    return filename

def extract_live_chat():
    json_path = ask_filename()  # Path to your JSON file
    csv_path = json_path+".csv"  # Desired path for the CSV file

    data = extract_data_from_json(json_path)
    write_to_csv(data, csv_path)
    print(f"Data written to '{csv_path}'")

def main():
    extract_live_chat()

if __name__ == "__main__":
    main()