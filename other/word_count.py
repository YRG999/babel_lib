# word_count.py

import re
from collections import Counter

def count_words(file_path, target_word):
    with open(file_path, 'r') as f:
        text = f.read().lower()
        words = re.findall(r'\b\w+\b', text)
        word_count = Counter(words)

    freq = word_count.get(target_word.lower(), 0)
    print(f"The word '{target_word}' appears {freq} times in the file.")

if __name__ == "__main__":

    file_path = input("File path? ")
    target_word = input("Target word? ")

    count_words(file_path, target_word)
