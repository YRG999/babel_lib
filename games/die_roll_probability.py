def predict_probability_and_rolls(sides):
    """
    Predicts the probability of rolling a specific target number on a die with a given number of sides
    and calculates the expected number of rolls to hit the target number.

    Parameters:
    sides (int): The number of sides on the die.

    Returns:
    float: The probability of rolling a specific number.
    int: The expected number of rolls to hit the target number.
    """
    probability = 1 / sides
    expected_rolls = sides  # The expected number of rolls to get the target number
    return probability, expected_rolls

# Example usage:
sides = int(input("Enter the number of sides on the die: "))
probability, expected_rolls = predict_probability_and_rolls(sides)
print(f"The probability of rolling any specific number on a {sides}-sided die is: {probability}.")
print(f"On average, it would take {expected_rolls} rolls to roll the target number on a {sides}-sided die.")
