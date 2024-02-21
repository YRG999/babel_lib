import requests
import random
import os
from dotenv import load_dotenv

def get_random_word():
    """Get a random word using the Random Word API by API Ninjas."""
    load_dotenv()
    API_NINJAS = os.getenv("API_NINJAS")

    api_url = "https://api.api-ninjas.com/v1/randomword"
    headers = {'X-Api-Key': API_NINJAS}  # Replace 'YOUR_API_KEY' with your actual API key from API Ninjas
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['word']
    else:
        print("Failed to retrieve word")
        return None

def generate_random_phrase(min_words=3, max_words=5):
    """Generate a random phrase using words from the Random Word API."""
    phrase_length = random.randint(min_words, max_words)
    words = [get_random_word() for _ in range(phrase_length)]
    phrase = ' '.join(words)
    return phrase

if __name__ == "__main__":
    # # Generate and print a random phrase
    # random_phrase = generate_random_phrase()
    # print(random_phrase)

    # Generate and print a random phrase five times
    for _ in range(5):
        random_phrase = generate_random_phrase()
        print(random_phrase)
