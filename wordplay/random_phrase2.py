# random_phrase2.py
# NEED TO DEBUG - NOT WORKING ANYMORE

import requests
import random
import os
from dotenv import load_dotenv

# def get_lorem_ipsum(api_key):
#     paragraphs = '2'
#     api_url = 'https://api.api-ninjas.com/v1/loremipsum?paragraphs={}'.format(paragraphs)
#     response = requests.get(api_url, headers={'X-Api-Key': 'YOUR_API_KEY'})
#     if response.status_code == requests.codes.ok:
#         print(response.text)
#     else:
#         print("Error:", response.status_code, response.text)

def get_random_word(api_key):
    """Get a random word using the Random Word API by API Ninjas."""
    load_dotenv()
    API_NINJAS = os.getenv("API_NINJAS")

    api_url = "https://api.api-ninjas.com/v1/randomword"
    # headers = {'X-Api-Key': api_key}
    headers = {'X-Api-Key': API_NINJAS}  # Replace 'YOUR_API_KEY' with your actual API key from API Ninjas
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        data = response.json()
        return data['word']
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def generate_random_phrase(min_words, max_words, api_key):
    """Generate a random phrase using words from the Random Word API."""
    phrase_length = random.randint(min_words, max_words)
    words = [get_random_word(api_key) for _ in range(phrase_length) if get_random_word(api_key)]
    phrase = ' '.join(words)
    return phrase

def random_phrase():
    load_dotenv()
    api_key = os.getenv("API_NINJAS")
    
    try:
        min_words = int(input("Enter the minimum number of words in the phrase: "))
        max_words = int(input("Enter the maximum number of words in the phrase: "))
        num_phrases = int(input("Enter the number of phrases to generate: "))

        if min_words > max_words:
            print("The minimum number of words cannot be greater than the maximum number of words.")
            return

        for _ in range(num_phrases):
            print(generate_random_phrase(min_words, max_words, api_key))
            
    except ValueError:
        print("Please enter valid integers for the minimum, maximum, and number of phrases.")

def main():
    random_phrase()

if __name__ == "__main__":
    main()