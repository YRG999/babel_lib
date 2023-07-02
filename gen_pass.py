import random
import string
import requests

def get_random_word():
    response = requests.get('https://random-word-api.herokuapp.com/word')
    if response.status_code == 200:
        data = response.json()
        word = data[0]  # Assuming the response is a list with a single word
        return word

    return None

def generate_passphrase():
    num_words = random.randint(3, 5)  # Random number of words in the passphrase
    words = [get_random_word() for _ in range(num_words)]
    words = [word.capitalize() for word in words if word is not None]

    # Capitalize 1-3 letters in each word
    for i in range(len(words)):
        word = words[i]
        num_letters_to_capitalize = random.randint(1, min(3, len(word)))
        random_indices = random.sample(range(len(word)), num_letters_to_capitalize)
        words[i] = ''.join(c.upper() if idx in random_indices else c for idx, c in enumerate(word))

    # Add a number between 0 and 9
    random_number = str(random.randint(0, 9))
    words.append(random_number)

    # Add an ASCII symbol
    ascii_symbols = string.punctuation
    random_symbol = random.choice(ascii_symbols)
    words.append(random_symbol)

    passphrase = ''.join(words)
    return passphrase

# Generate a passphrase
passphrase = generate_passphrase()

# Output the passphrase
print("Passphrase:", passphrase)
