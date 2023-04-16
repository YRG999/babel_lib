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

with open('output/generated_sentences.txt', 'a') as file:
    for _ in range(100):
        sentence = generate_sentence()
        file.write(sentence + '\n')
        print(sentence)

print('Sentences saved to generated_sentences.txt.')
