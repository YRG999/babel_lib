import random
import string

def generate_word():
    letters = string.ascii_lowercase + ',. '
    word = ''.join(random.choice(letters) for _ in range(random.randint(1, 10)))
    return word.capitalize()

def generate_sentence():
    num_words = random.randint(1, 10)
    words = [generate_word() for _ in range(num_words)]
    sentence = ' '.join(words) + random.choice(['.', '!', '?'])
    return sentence

for _ in range(10):
    print(generate_sentence())
