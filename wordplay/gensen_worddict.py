# generate_sentence4.py

import random
import language_tool_python
import requests

# Initialize the LanguageTool grammar checker
tool = language_tool_python.LanguageToolPublicAPI('en-US') # use the public API

def get_random_word():
    response = requests.get('https://random-word-api.herokuapp.com/word')
    if response.status_code == 200:
        data = response.json()
        word = data[0]  # Assuming the response is a list with a single word
        return word

    return None

def generate_sentence():
    num_words = random.randint(3, 6)  # Random number of words in the sentence
    words = [get_random_word() for _ in range(num_words)]
    words = [word.capitalize() for word in words if word is not None]
    sentence = ' '.join(words) + '.'  # Add a period at the end
    return sentence

def validate_sentence(sentence):
    matches = tool.check(sentence)
    return len(matches) == 0

def generate_and_validate_sentence():
    invalid_counter = 0
    while True:
        sentence = generate_sentence()
        if validate_sentence(sentence):
            return sentence
        else:
            invalid_counter += 1
            print("Invalid Sentence:", sentence, "Count:", invalid_counter)

def main():
    # Generate and validate a sentence
    valid_sentence = generate_and_validate_sentence()

    # Output the valid sentence
    print("Valid Sentence:", valid_sentence)

if __name__ == "__main__":
    main()