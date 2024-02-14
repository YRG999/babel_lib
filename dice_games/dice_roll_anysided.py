# roll a die with the number of sides specified by the user
# created with claude.ai

import random

print("Let's roll a die!")
sides = int(input("How many sides? "))

rolling = True
while rolling:
    roll = random.randint(1, sides)
    print("You rolled a", roll)
    
    repeat = input("Press ENTER to roll again or n and ENTER to stop. ")
    if repeat.lower() == "n":
        rolling = False

print("Thanks for playing!")