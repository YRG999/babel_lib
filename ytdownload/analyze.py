# analyze_chat7.py
# optimize code

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import re
from typing import Dict, Any, Tuple, Optional

def parse_superchat_value(message):
    match = re.search(r'([\$€£¥])(\d+(?:\.\d{2})?)', message)
    if match:
        currency = match.group(1)
        value = float(match.group(2))
        return currency, value
    return None, 0

def seconds_to_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

# Refactored with generater expression and helper function
def analyze_csv(filename: str) -> Tuple[int, Dict[str, float], Dict[str, int], float]:
    superchats = 0
    superchat_values = defaultdict(float)
    author_counts = defaultdict(int)
    messages = []

    def process_row(row: Dict[str, Any], row_num: int) -> Optional[Tuple[str, str, datetime, Optional[Tuple[str, float]]]]:
        """
        Processes a single CSV row and extracts necessary information.

        Parameters:
            row (Dict[str, Any]): The CSV row as a dictionary.
            row_num (int): The current row number for error reporting.

        Returns:
            Optional[Tuple[str, str, datetime, Optional[Tuple[str, float]]]]:
                - message (str)
                - author (str)
                - timestamp (datetime)
                - superchat_info (Tuple[str, float]) if the message is a superchat, else None
        """
        try:
            message = row.get('Message', '').strip()
            author = row.get('Author', '').strip()
            timestamp_str = row.get('Timestamp', '').strip()
            
            # Validate required fields
            if not all([message, author, timestamp_str]):
                print(f"Warning: Incomplete data in row {row_num}: {row}")
                return None

            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

            # Initialize superchat_info as None
            superchat_info = None

            # Check if the message is a Superchat
            if message.startswith('[Superchat'):
                currency, value = parse_superchat_value(message)
                if currency and value:
                    superchat_info = (currency, value)
                else:
                    print(f"Warning: Unable to parse Superchat value in row {row_num}: {message}")
            
            return (message, author, timestamp, superchat_info)
        
        except Exception as e:
            print(f"Error processing row {row_num}: {row}. Error: {e}")
            return None

    # Open and read the CSV file
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Create a generator expression to process each row
        processed_rows = (
            process_row(row, row_num)
            for row_num, row in enumerate(reader, start=1)
        )

        # Iterate over the generator to update counts and lists
        for processed in processed_rows:
            if processed is None:
                continue  # Skip rows with incomplete data or processing errors
            
            message, author, timestamp, superchat_info = processed

            # Update author message count
            author_counts[author] += 1

            # Append message and timestamp
            messages.append((message, timestamp))

            # If it's a Superchat, update Superchat counts and values
            if superchat_info:
                superchats += 1
                currency, value = superchat_info
                superchat_values[currency] += value

    # Calculate total time in seconds between first and last message
    if messages:
        sorted_messages = sorted(messages, key=lambda x: x[1])
        total_time = (sorted_messages[-1][1] - sorted_messages[0][1]).total_seconds()
    else:
        total_time = 0.0

    return superchats, superchat_values, author_counts, total_time

def generate_markdown_table(data):
    superchats, superchat_values, author_counts, total_time = data

    markdown = "| Metric | Value |\n|--------|-------|\n"
    markdown += f"| Total Superchats | {superchats} |\n"
    for currency, value in superchat_values.items():
        markdown += f"| Total Superchat Value ({currency}) | {currency}{value:.2f} |\n"
    markdown += f"| Total Time | {seconds_to_hms(total_time)} (HH:MM:SS) |\n"
    markdown += f"| Total Time (seconds) | {total_time:.2f} |\n\n"

    markdown += "| Author | Message Count |\n|--------|---------------|\n"
    
    # Sort authors by message count in descending order
    sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
    
    for author, count in sorted_authors:
        markdown += f"| {author} | {count} |\n"

    return markdown

def main():
    input_file = input("Live chat CSV filename? ")
    output_file = input_file+'_analysis_results.md'

    try:
        data = analyze_csv(input_file)
        markdown_table = generate_markdown_table(data)

        with open(output_file, 'w') as file:
            file.write(markdown_table)

        print(f"Analysis complete. Results saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




