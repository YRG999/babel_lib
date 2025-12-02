# word_count.py

import re
from collections import Counter

def count_words(file_path, target_word):
    # Optimized: stream processing instead of loading entire file into memory
    word_count = Counter()
    target_lower = target_word.lower()
    
    with open(file_path, 'r') as f:
        for line in f:
            # Process line by line for better memory efficiency with large files
            words = re.findall(r'\b\w+\b', line.lower())
            word_count.update(words)

    freq = word_count.get(target_lower, 0)
    print(f"The word '{target_word}' appears {freq} times in the file.")

if __name__ == "__main__":

    file_path = input("File path? ")
    target_word = input("Target word? ")

    count_words(file_path, target_word)
