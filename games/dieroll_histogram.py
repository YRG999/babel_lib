# dieroll_histogram6.py
# codellama
# simplest version, only imports random

import random

def main():
    # Create an empty dictionary to store the results
    results = {}

    # Simulate rolling the die 1000 times
    for i in range(1000):
        # Roll the die and get the result
        result = random.randint(1, 6)

        # Increment the count for this result
        results[result] = results.get(result, 0) + 1

    # Print the histogram of the results
    print("Histogram of die rolls:")
    for i in range(1, 7):
        print(f"{i}: {results.get(i, 0)}")

if __name__ == "__main__":
    main()

