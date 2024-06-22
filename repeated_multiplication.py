# repeated_multiplication.py

import random
import csv

def generate_and_modify_number():
    """Generates a random number, modifies it, and returns the result."""
    random_number = random.randint(1, 100)
    result = random_number * 10
    result = result // 10  # Remove the last digit
    return result

def main():
    """Controls the main program flow."""
    numbers = []
    num_iterations = int(input("How many numbers would you like to generate? "))

    for _ in range(num_iterations):
        number = generate_and_modify_number()
        numbers.append(number)
        print(number)

    # Save to CSV
    with open('random_numbers.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(numbers)

    print("Numbers saved to 'random_numbers.csv'")

if __name__ == "__main__":
    main()
