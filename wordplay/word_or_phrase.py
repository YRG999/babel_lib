from random_phrase2 import *
from define_word2 import *

def user_choice():
    choice = input("Do you want to (1) generate a random phrase or (2) define a word? Enter 1 or 2: ")
    return choice
    
def main():
    choice = user_choice()
    
    if choice == '1':
        random_phrase()

    elif choice == '2':
        define_word()

if __name__ == "__main__":
    main()
