# claude.ai
# ValueError: shape mismatch: objects cannot be broadcast to a single shape.  Mismatch is between arg 0 with shape (6,) and arg 1 with shape (7,).
# after the bug was fixed, this worked nicely!

import matplotlib.pyplot as plt
import numpy as np

# Simulate rolling a 6-sided die 1000 times
rolls = np.random.randint(1, 7, 1000)

# Get the counts for each die roll value
# counts = np.bincount(rolls)
counts, _ = np.histogram(rolls, bins=6)

# # Set the x-axis labels
# x_labels = list(range(1, 7))

# # Plot a histogram with 6 bars (one for each side of the die)
# plt.bar(x_labels, counts)

# Set the x coordinates for the bars
x_pos = np.arange(len(counts))

# Plot the bars 
plt.bar(x_pos, counts, align='center')

# Set ticks and labels  
plt.xticks(x_pos, np.arange(1, 7))  

# Set title and axis labels
plt.title("Results of Rolling a 6-Sided Die 1000 Times")  
plt.xlabel("Die Roll Value")
plt.ylabel("Count")

plt.show()