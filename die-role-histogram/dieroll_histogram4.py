# dolphin-mixtral:8x7b-v2.5-q2_K
import numpy as np
import matplotlib.pyplot as plt

# Function to create a histogram from the results
def roll_dice():
    # List for storing results
    results = []

    # Loop 1000 times
    for _ in range(1000):
        results.append(np.random.randint(1, 7))
    
    # Create a histogram of the results
    plt.hist(results)
    plt.title("Histogram of Die Results")
    plt.xlabel("Side Number")
    plt.ylabel("Frequency")
    plt.grid(True)
    
    # Show plot
    plt.show()

# Test the function
roll_dice()
