# count-livechat2.py
# This script counts the number of messages per author in a CSV file containing live chat data.
# It prompts the user for the file path and logs the results to a text file with a timestamp.
import pandas as pd
from datetime import datetime

# Ask the user for the file path
file_path = input("Enter the path to the chat log CSV file: ")

# Load the CSV file
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print("Error: File not found. Please check the file path and try again.")
    exit()

# Count the number of messages per author
author_counts = data['Author'].value_counts()

# Log the results to a text file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"chat_log_summary_{timestamp}.txt"

with open(output_file, "w") as f:
    f.write("Chat Log Summary\n")
    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Source File: {file_path}\n\n")
    f.write(author_counts.to_string())

print(f"Results have been logged to {output_file}")