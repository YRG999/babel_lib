import random
import matplotlib.pyplot as plt

def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)

rolls = [roll_dice() for _ in range(100)]
plt.hist(rolls, bins=range(2, 14), align='left', rwidth=0.8)
plt.xticks(range(2, 13))
plt.xlabel('Roll')
plt.ylabel('Frequency')
plt.title('Histogram of 2d6 Rolls')
plt.show()
