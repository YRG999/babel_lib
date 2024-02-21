from random_phrase2 import *

def get_word_definition(word, api_key):
    """Fetch the definition of a word using the API."""
    api_url = f'https://api.api-ninjas.com/v1/dictionary?word={word}'
    try:
        response = requests.get(api_url, headers={'X-Api-Key': api_key})
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        data = response.json()
        # Check if the word is valid and has a definition
        if data.get('valid', False):
            return data['definition'] if data['definition'] else "No definition found."
        else:
            return f"The word '{word}' is not valid or not found."
    except requests.RequestException as e:
        return f"Request failed: {e}"

def ask_for_definition(api_key):
    """Ask the user if they want the definition of a word, then fetch and print it."""
    while True:
        want_definition = input("Do you want the definition of a word? (yes/no): ").lower()
        if want_definition == 'yes':
            word = input("Enter the word: ")
            definition = get_word_definition(word, api_key)
            print(f"Definition of {word}: {definition}")
        elif want_definition == 'no':
            break
        else:
            print("Please answer with 'yes' or 'no'.")

def main():
    load_dotenv()
    api_key = os.getenv("API_NINJAS")
    
    ask_for_definition(api_key)

if __name__ == "__main__":
    main()
