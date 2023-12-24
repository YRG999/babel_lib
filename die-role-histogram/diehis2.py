# from https://chat.lmsys.org/?arena
# via https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard
# chatgpt or claude

import matplotlib.pyplot as plt
import random

# Simulate rolling a 6-sided die 1000 times
rolls = [random.randint(1, 6) for i in range(1000)]

# Count the number of times each value appears
counts = [rolls.count(i) for i in range(1, 7)]

# Set the x-axis labels
x = list(range(1, 7))

# Plot a histogram with title and labels
plt.bar(x, counts)
plt.title("Results of Rolling a 6-Sided Die 1000 Times")  
plt.xlabel("Value")
plt.ylabel("Frequency")

plt.show()