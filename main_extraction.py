import json
import csv
from extract_functions import extract_message, extract_emoji, extract_authorname, extract_timestamp, convert_to_eastern

def ask_filename():
    print("Name or path of file to extract")
    filename = input()
    return filename

def extract_data_from_json(json_path):
    data_list = []
    
    # Load each JSON object separately, ignoring whitespace between them
    with open(json_path, 'r') as json_file:
        decoder = json.JSONDecoder()
        file_content = json_file.read()
        idx = 0
        while idx < len(file_content):
            try:
                obj, idx = decoder.raw_decode(file_content, idx)
                data_list.append(obj)
            except json.JSONDecodeError:
                idx += 1  # Skip over any whitespace or unexpected characters
    
    # Extract required data
    extracted_data = []
    for data in data_list:
        actions = data.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            item = action.get('addChatItemAction', {}).get('item', {}).get('liveChatTextMessageRenderer', {})
            message = extract_message(item)
            emoji = extract_emoji(item)
            authorname = extract_authorname(item)
            timestamp = extract_timestamp(item)
            eastern_time = convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            extracted_data.append([message, emoji, authorname, eastern_time])
    
    return extracted_data

def write_to_csv(data, csv_path):
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Message", "Emoji", "AuthorName", "Eastern Time"])
        writer.writerows(data)

if __name__ == "__main__":
    # json_path = "test555.json"  # Path to your JSON file
    # csv_path = "output.csv"  # Desired path for the CSV file
    json_path = ask_filename()  # Path to your JSON file
    csv_path = json_path+".csv"  # Desired path for the CSV file

    data = extract_data_from_json(json_path)
    write_to_csv(data, csv_path)
    print(f"Data written to '{csv_path}'")
