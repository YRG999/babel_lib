# analyze_chat8.py
# This script analyzes a CSV file containing live chat data from YouTube.
# It counts the number of superchats, calculates their total value,
# and counts the number of messages sent by each author.
# It generates a markdown table with the results.
# added logging functionality to track errors and warnings

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import re
from typing import Dict, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    filename='analyze.log',  # Log file name
    level=logging.DEBUG,     # Log all levels (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_superchat_value(message):
    match = re.search(r'([\$€£¥])(\d+(?:\.\d{2})?)', message)
    if match:
        currency = match.group(1)
        value = float(match.group(2))
        return currency, value
    return None, 0

def seconds_to_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

# Refactored with generator expression and helper function
def analyze_csv(filename: str) -> Tuple[int, Dict[str, float], Dict[str, int], float]:
    superchats = 0
    superchat_values = defaultdict(float)
    author_counts = defaultdict(int)
    # Optimization: Track min/max timestamps instead of storing all messages
    first_timestamp = None
    last_timestamp = None

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
                logging.warning(f"Incomplete data in row {row_num}: {row}")
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
                    logging.warning(f"Unable to parse Superchat value in row {row_num}: {message}")
            
            return (message, author, timestamp, superchat_info)
        
        except Exception as e:
            logging.error(f"Error processing row {row_num}: {row}. Error: {e}")
            return None

    # Open and read the CSV file
    try:
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

                # Optimization: Track first and last timestamp without storing all messages
                if first_timestamp is None or timestamp < first_timestamp:
                    first_timestamp = timestamp
                if last_timestamp is None or timestamp > last_timestamp:
                    last_timestamp = timestamp

                # If it's a Superchat, update Superchat counts and values
                if superchat_info:
                    superchats += 1
                    currency, value = superchat_info
                    superchat_values[currency] += value

        # Calculate total time in seconds between first and last message
        if first_timestamp and last_timestamp:
            total_time = (last_timestamp - first_timestamp).total_seconds()
        else:
            total_time = 0.0

        return superchats, superchat_values, author_counts, total_time

    except Exception as e:
        logging.error(f"Error reading file {filename}: {e}")
        raise

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
        logging.error(f"An error occurred during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()