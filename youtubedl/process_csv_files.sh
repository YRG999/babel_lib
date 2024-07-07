#!/bin/bash

# Set the directory containing the CSV files to the current directory
csv_dir="."

# Set the directory for output markdown files to a subdirectory named 'output'
output_dir="./chatoutput"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all CSV files in the directory
for file in "$csv_dir"/*.csv; do
    # Get the filename without extension
    filename=$(basename "$file" .csv)
    
    # Run the Python script for each CSV file
    python3 analyze_chat_batch.py "$file" "$output_dir/${filename}_analysis.md"
done

echo "All CSV files have been processed."

# To run:
# Open Terminal and navigate to the directory containing your CSV files and the scripts:
# cd /path/to/your/directory

# Make the shell script executable:
# chmod +x process_csv_files.sh

# Run the shell script:
# ./process_csv_files.sh