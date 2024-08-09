# countletters2
# see [mistral notes](more/mistral20240725.md)

def char_count(string):
    result = {}
    for letter in string:
        if letter.isalpha() or letter == " ":  # skip non-alphabetic characters
            if letter not in result:
                result[letter] = 1
            else:
                result[letter] += 1
    return result

word = input("word? ")
print(char_count(word))