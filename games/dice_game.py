# dice_game_4b.py

import random

def roll_dice(num_dice, sides=6):
    return [random.randint(1, sides) for _ in range(num_dice)]

def buy_dice(money, dice_price):
    choice = input(f"Do you want to buy an extra die for {dice_price} (yes/no)? ").lower()
    if choice == 'yes' and money >= dice_price:
        money -= dice_price
        return True, money
    return False, money

def game4():
    turns = 10
    level = 1
    levels_difficulty = [6, 8, 10, 12, 14]
    treasure_value = 0
    money = 100  # Starting money
    regular_dice_price = 20
    special_dice_price = 50
    special_dice = []

    print("Welcome to Treasure Hunter! Find treasure parts to increase your treasure's value.\n")

    while turns > 0 and level <= 5:
        print(f"Level: {level}, Turns left: {turns}, Money: {money}, Treasure Value: {treasure_value}, Special Dice Available: {len(special_dice)}")
        
        # Option to buy regular dice
        bought_dice, money = buy_dice(money, regular_dice_price)
        dice_choice = 1 + int(bought_dice)  # Always have at least 1 die, add more if bought
        
        # Option to buy special dice
        if money >= special_dice_price:
            bought_special_dice, money = buy_dice(money, special_dice_price)
            if bought_special_dice:
                special_dice.append(8)  # Assuming D8 for special dice
                print("You bought a special D8 dice!")

        roll_sum = sum(roll_dice(dice_choice)) + sum(roll_dice(len(special_dice), 8))  # Roll special dice
        print(f"You rolled a total of: {roll_sum}")

        if roll_sum >= levels_difficulty[level - 1]:
            print("You found the treasure part on this level and advance to the next level!")
            level += 1
            treasure_value += 100 * level  # Increase treasure value
        else:
            print("You didn't find the treasure part this turn.")
        
        # Encounter a trap
        if random.random() < 0.2:  # 20% chance
            trap_effect = random.choice(['dice', 'turn'])
            if trap_effect == 'dice' and special_dice:
                special_dice.pop()
                print("A trap has taken one of your special dice!")
            else:
                turns -= 1
                print("A trap has cost you a turn!")

        turns -= 1
        print("")

    if level > 5:
        print(f"Congratulations! You've found the treasure worth {treasure_value} and won the game!")
    else:
        print(f"Unfortunately, you've run out of turns before finding the treasure worth {treasure_value}. Better luck next time!")

if __name__ == "__main__":
    game4()
