# analyze_chat7-batch.py
# separate currencies
# sort author by message count
# add batch file capabilities

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sys

def parse_superchat_value(message):
    match = re.search(r'([\$€£¥])(\d+(?:\.\d{2})?)', message)
    if match:
        currency = match.group(1)
        value = float(match.group(2))
        return currency, value
    return None, 0

def seconds_to_hms(seconds):
    return str(timedelta(seconds=int(seconds)))

def analyze_csv(filename):
    superchats = 0
    superchat_values = defaultdict(float)
    author_counts = defaultdict(int)
    messages = []

    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader, start=1):
            try:
                message = row.get('Message', '')
                author = row.get('Author', '')
                timestamp_str = row.get('Timestamp', '')
                
                if not all([message, author, timestamp_str]):
                    print(f"Warning: Incomplete data in row {row_num}: {row}")
                    continue

                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                author_counts[author] += 1
                messages.append((message, timestamp))

                if message.startswith('[Superchat'):
                    superchats += 1
                    currency, value = parse_superchat_value(message)
                    if currency:
                        superchat_values[currency] += value
            except Exception as e:
                print(f"Error processing row {row_num}: {row}. Error: {e}")
                continue

    if messages:
        total_time = (messages[-1][1] - messages[0][1]).total_seconds()
    else:
        total_time = 0

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

def main(input_file, output_file):
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
    if len(sys.argv) != 3:
        print("Usage: python analyze_chat.py <input_csv_file> <output_md_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)