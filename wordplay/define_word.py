# define_word2.py

from random_phrase import *
import csv

def fetch_word_data(word, api_key):
    """Fetch word data from the API and cache the response."""
    api_url = f'https://api.api-ninjas.com/v1/dictionary?word={word}'
    try:
        response = requests.get(api_url, headers={'X-Api-Key': api_key})
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def is_word_valid(cached_response):
    """Determine if the word is valid using the cached API response."""
    if cached_response is not None:
        return cached_response.get('valid', False)
    return False

def get_definition_from_cached_response(cached_response):
    """Get the word's definition from the cached API response, if valid."""
    if cached_response and cached_response.get('valid', False):
        return cached_response.get('definition', "No definition found.")
    return "No definition found because the word is not valid or the data is unavailable."

def save_word_to_csv(word, definition, filename='output/word_definitions.csv'):
    """Save the word and its definition to a CSV file."""
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([word, definition])

def define_word():
    load_dotenv()
    api_key = os.getenv("API_NINJAS")
    word = input("Enter a word to get its definition: ")
    # Initialize definition variable to ensure it's always defined
    definition = "Definition not found or word is invalid."

    # Fetch and cache the API response
    cached_response = fetch_word_data(word, api_key)
    
    # Check if the word is valid using the cached response
    if is_word_valid(cached_response):
        definition = get_definition_from_cached_response(cached_response)
        print(f"Definition of {word}: {definition}")
    else:
        print(f"The word '{word}' is not valid or no data is available.")

    save_word_to_csv(word, definition)

def main():
    define_word()

if __name__ == "__main__":
    main()
