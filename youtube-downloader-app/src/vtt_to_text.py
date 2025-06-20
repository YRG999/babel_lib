import os
import re
from html import unescape

def clean_line(line):
    # Remove HTML tags
    line = re.sub(r'<.*?>', '', line)
    # Unescape HTML entities
    line = unescape(line)
    # Remove extra whitespace
    return line.strip()

def vtt_to_text(vtt_file_path):
    with open(vtt_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    text_lines = []
    last_line = None
    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT":
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        cleaned = clean_line(line)
        if cleaned and cleaned != last_line:
            text_lines.append(cleaned)
            last_line = cleaned

    # Join with newlines for plain text output
    plain_text = '\n'.join(text_lines)

    # Save with same name and location, but .txt extension
    base, _ = os.path.splitext(vtt_file_path)
    output_file_path = base + ".txt"
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)
    print(f"Transcript saved to: {output_file_path}")

if __name__ == "__main__":
    vtt_file = input("Enter the path to the VTT file: ").strip()
    vtt_to_text(vtt_file)