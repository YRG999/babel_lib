import random

def game1():
    print("Game 1: Let's roll a die!")
    sides = int(input("How many sides? "))

    rolling = True
    while rolling:
        roll = random.randint(1, sides)
        print("You rolled a", roll)
        
        repeat = input("Press ENTER to roll again or n and ENTER to stop. ")
        if repeat.lower() == "n":
            rolling = False

    print("Thanks for playing Game 1!")

def game2():
    print("Game 2: Roll until you hit the same number again!")
    sides = int(input("How many sides? "))
    target_roll = random.randint(1, sides)
    print(f"Your target roll is: {target_roll}")

    roll_count = 1
    while True:
        roll = random.randint(1, sides)
        print(f"Roll {roll_count}: You rolled a {roll}")
        if roll == target_roll:
            print(f"It took {roll_count} rolls to hit the target roll again.")
            break
        roll_count += 1

    print("Thanks for playing Game 2!")

def main():
    choice = input("Which game would you like to play? Enter 1 for Game 1 or 2 for Game 2: ")
    if choice == "1":
        game1()
    elif choice == "2":
        game2()
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
