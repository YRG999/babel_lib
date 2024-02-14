import random
import matplotlib.pyplot as plt

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

def game2(sides=None, silent=False):
    if not sides:
        sides = int(input("How many sides? "))
    target_roll = random.randint(1, sides)
    if not silent:
        print(f"Game 2: Roll until you hit the same number again!\nYour target roll is: {target_roll}")

    roll_count = 1
    while True:
        roll = random.randint(1, sides)
        if roll == target_roll:
            if not silent:
                print(f"It took {roll_count} rolls to hit the target roll again.")
            break
        roll_count += 1

    if not silent:
        print("Thanks for playing Game 2!")
    return roll_count

def game3():
    print("Game 3: Play Game 2 multiple times and display a graph of the results.")
    sides = int(input("How many sides? "))
    times = int(input("How many times to play? "))

    results = [game2(sides, silent=True) for _ in range(times)]

    plt.plot(range(1, times+1), results, marker='o', linestyle='-')
    plt.title('Game 2 Roll Counts Over Multiple Plays')
    plt.xlabel('Game Instance')
    plt.ylabel('Number of Rolls to Match Target Roll')
    plt.grid(True)
    plt.show()

    print("Thanks for playing Game 3!")

def main():
    choice = input("Which game would you like to play?\n1. Roll a die\n2. Roll a die and try and roll the same number again\n3. Roll a die and try to roll the same number again multiple times\n")
    if choice == "1":
        game1()
    elif choice == "2":
        game2()
    elif choice == "3":
        game3()
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
