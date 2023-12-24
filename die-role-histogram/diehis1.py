# from https://chat.lmsys.org/?arena
# via https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard
# chatgpt or claude

import random
from collections import Counter
import matplotlib.pyplot as plt

def roll_die():
    return random.randint(1, 6)

def simulate_rolls(num_rolls):
    rolls = [roll_die() for _ in range(num_rolls)]
    return Counter(rolls)

def create_histogram(roll_counts):
    labels, values = zip(*roll_counts.items())
    plt.bar(labels, values)
    plt.xlabel('Die Face')
    plt.ylabel('Frequency')
    plt.title('Histogram of 1000 Die Rolls')
    plt.show()

if __name__ == "__main__":
    num_rolls = 1000
    roll_counts = simulate_rolls(num_rolls)
    create_histogram(roll_counts)