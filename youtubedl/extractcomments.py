import json
import csv
import datetime
import pytz

def convert_to_eastern(timestamp):
    # Convert Unix timestamp to naive UTC datetime
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    
    # Make the UTC datetime timezone-aware
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    
    # Convert to Eastern Time
    eastern_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
    
    return eastern_time

def extract_comments():

    # ask for file
    json_file = input("Enter file path\n")

    # 1. Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # 2. Traverse the JSON data
    comments = data['comments']
    extracted_data = []
    for comment in comments:
        comment_id = comment['id']
        text = comment['text']
        author = comment['author']
        timestamp = comment['timestamp']
        eastern_time = convert_to_eastern(timestamp)
        extracted_data.append([comment_id, text, author, timestamp, eastern_time.strftime('%Y-%m-%d %H:%M:%S')])

    # 3. Write the extracted data to a CSV file
    with open(json_file+'-output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Text", "Author", "Timestamp", "Eastern Time"])  # Writing the headers
        writer.writerows(extracted_data)

def main():
    extract_comments()

if __name__ == "__main__":
    main()