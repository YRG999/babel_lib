# extract_chatsuperemoji.py
# Run this on live_chat JSON file to extract regular and paid chats.

from youtube_functions import * 
import csv
import json
import os
import emoji
import json
import logging

def is_emoji(text):
    return emoji.is_emoji(text)

def extract_text_and_emoji(data):
    """Extract text emoji or shortcut. Check valid emoji using the emoji library."""
    message_runs = data.get('message', {}).get('runs', [])
    output_elements = []
    
    for run in message_runs:
        if 'text' in run:
            output_elements.append(run['text'])
        elif 'emoji' in run:
            if 'emojiId' in run['emoji'] and is_emoji(run['emoji']['emojiId']):
                output_elements.append(run['emoji']['emojiId'])
            elif 'shortcuts' in run['emoji']:
                output_elements.append(run['emoji']['shortcuts'][0])
            else:
                output_elements.append("[Unknown]")
    
    return ''.join(output_elements)

def get_json_data(filename=None):
    if filename is None:
        filename = input("Enter the name of the JSON file: ")
    
    try:
        with open(filename, "r") as f:
            data_list = [
                json.loads(line.strip())
                for line in f
            ]
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in file {filename}: {e}")
        return [], filename
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return [], filename
    
    return data_list, filename

def extract_data_from_json(json_data, json_path=None):
    '''
    Extracts live chat data from JSON data.

    Args:
        json_data: The JSON data to process.
        json_path: Optional. The path to the JSON file. Defaults to None.

    Returns:
        List of extracted data.
    '''
    extracted_data = []
    for data in json_data:
        actions = data.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            item = action.get('addChatItemAction', {}).get('item', {})
            
            # Check for liveChatTextMessageRenderer or liveChatPaidMessageRenderer
            text_renderer = item.get('liveChatTextMessageRenderer')
            paid_renderer = item.get('liveChatPaidMessageRenderer')
            
            if text_renderer or paid_renderer:
                chat_renderer = text_renderer or paid_renderer
                authorname = chat_renderer.get('authorName', {}).get('simpleText', '')
                message = extract_text_and_emoji(chat_renderer)
                
                # Handle Superchat
                if paid_renderer:
                    purchase_amount = paid_renderer.get('purchaseAmountText', {}).get('simpleText', '')
                    message = f"[Superchat {purchase_amount}] " + message
                
                timestamp = extract_timestamp(chat_renderer)
                eastern_time = convert_to_eastern(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                extracted_data.append([message, authorname, eastern_time])
    
    return extracted_data

def save_to_csv(data, output_filename):
    """
    Saves the extracted data to a CSV file.
    
    :param data: List of lists containing the extracted data
    :param output_filename: Name of the output CSV file
    """
    # Ensure the filename ends with .csv
    if not output_filename.lower().endswith('.csv'):
        output_filename += '.csv'
    
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the full path for the output file
    output_path = os.path.join(script_dir, output_filename)
    
    # Write the data to the CSV file
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write the header
        csv_writer.writerow(['Message', 'Author', 'Timestamp'])
        
        # Write the data
        csv_writer.writerows(data)
    
    print(f"Data saved to {output_path}")

def main():
    json_data, filename = get_json_data()
    result = extract_data_from_json(json_data, filename)
    
    # Generate output filename based on input filename
    output_filename = os.path.splitext(filename)[0] + "_extracted.csv"
    
    save_to_csv(result, output_filename)

if __name__ == "__main__":
    main()
