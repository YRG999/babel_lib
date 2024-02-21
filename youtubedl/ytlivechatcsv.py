# ytlivechatcsv.py
# Run if ytlivechatcommentdl.py fails to convert live chat JSON file to CSV.
# Does the same thing as main_extraction.py

from youtube_functions import *

def convert_livechat_to_csv():
    json_path = "PATH_TO_JSON"  # Replace with path to your live chat JSON file

    ## check to see if there is a downloaded livechat JSON file
    csv_path = json_path+".csv"  # Name CSV file by added extension to JSON file
    data = extract_data_from_json(json_path) # Extract data from live_chat.json
    write_to_csv(data, csv_path) # Write to live_chat.json.csv
    print(f"Data written to '{csv_path}'") # Print the name of the CSV file to the console

def main():
    convert_livechat_to_csv()

if __name__ == "__main__":
    main()