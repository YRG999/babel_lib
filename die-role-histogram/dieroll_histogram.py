# ollama magicoder
import random
import matplotlib.pyplot as plt

# Initialize an empty list to store die roll results
die_rolls = []

# Simulate 1000 dice rolls and add the result (a number between 1 and 6) to the list
for _ in range(100):
    die_rolls.append(random.randint(1, 6))

# Create a histogram of the die roll results
# plt.hist(die_rolls, bins=range(7), align='left', edgecolor='black')
plt.hist(die_rolls, bins=range(1, 8), align='left', edgecolor='black')
plt.xticks([1,2,3,4,5,6]) # Set x-tick labels to be the number on each side of the die
plt.xlabel('Value on a 6-sided die')
plt.ylabel('Frequency')
plt.title('Histogram of 1000 dice rolls')
plt.show()
