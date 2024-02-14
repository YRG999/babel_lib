import random

def roll_dice(num_dice, sides=6):
    return [random.randint(1, sides) for _ in range(num_dice)]

def game4():
    turns = 10
    level = 1
    levels_difficulty = [6, 8, 10, 12, 14]
    special_dice = []

    print("Welcome to Treasure Hunter!\n")

    while turns > 0 and level <= 5:
        print(f"Level: {level}, Turns left: {turns}, Special Dice Available: {len(special_dice)}")
        dice_choice = int(input("How many regular D6 dice to roll (1-3)? "))
        special_dice_choice = int(input(f"How many special dice to use (0-{len(special_dice)})? "))
        
        if special_dice_choice > len(special_dice):
            print("You don't have enough special dice. Using available ones.")
            special_dice_choice = len(special_dice)
        
        roll_sum = sum(roll_dice(dice_choice)) + sum(roll_dice(special_dice_choice, 8))  # Assuming D8 for special dice
        special_dice = special_dice[special_dice_choice:]
        
        print(f"You rolled a total of: {roll_sum}")
        
        if roll_sum >= levels_difficulty[level - 1]:
            print("You found the treasure part on this level and advance to the next level!")
            level += 1
            # Chance to find a special dice
            if random.random() < 0.3:  # 30% chance
                special_dice.append(8)  # Add a D8
                print("You found a special D8 dice!")
        else:
            print("You didn't find the treasure part this turn.")
        
        # Encounter a trap (20% chance)
        if random.random() < 0.2:
            if random.random() < 0.5 and special_dice:
                special_dice.pop()
                print("Oh no! A trap has taken one of your special dice!")
            else:
                turns -= 1
                print("Oh no! A trap has cost you a turn!")

        turns -= 1
        print("")

    if level > 5:
        print("Congratulations! You've found the treasure and won the game!")
    else:
        print("Unfortunately, you've run out of turns before finding the treasure. Better luck next time!")

if __name__ == "__main__":
    game4()
