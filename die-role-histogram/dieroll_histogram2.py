# chatgpt
# best one so far

import matplotlib.pyplot as plt
import random

# Simulating the roll of a 6-sided die 1000 times
rolls = [random.randint(1, 6) for _ in range(1000)]

# Creating a histogram of the results
plt.hist(rolls, bins=range(1, 8), edgecolor='black', align='left')
plt.title('Histogram of 1000 Die Rolls')
plt.xlabel('Die Value')
plt.ylabel('Frequency')
plt.xticks(range(1, 7))
plt.show()
