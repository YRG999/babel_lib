# extracts text and emoji from youtube live chat

# from youtube_functions import (
#     extract_data_from_json, 
#     write_to_csv)

# print("Enter JSON file to extract live chat comments from: ")
# json_file = input()

# data = extract_data_from_json(json_file) # Extract data from *live_chat.json
# write_to_csv(data, json_file+".csv") # Write to *live_chat.json.csv
# print(f"Data written to {json_file}.csv") # Print the name of the CSV file to the console

# Updated
from ytdl_updated import livechat_to_csv

print("Enter file path to live chat file: ")
livechat_file = input()

livechat_csv = livechat_to_csv(livechat_file)
print(f"Live chat saved as: {livechat_csv}")
