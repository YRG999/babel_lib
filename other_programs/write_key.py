import json
import os

def create_library_file_if_not_exists():
  """Creates the library file `library.json` if it doesn't exist."""
  if not os.path.exists("output/library.json"):
    with open("output/library.json", "w") as f:
      json.dump({}, f)

def load_library(filename):
  """Loads the library from a JSON file."""
  with open(filename, "r") as f:
    library = json.load(f)
  return library

def save_library(library, filename):
  """Saves the library to a JSON file."""
  with open(filename, "w") as f:
    json.dump(library, f)

def get_user_input():
  """Gets user input for a key."""
  key = input("Enter a key: ")
  return key

def check_library_for_key(library, key):
  """Checks the library for a key."""
  if key in library:
    return True
  else:
    return False

def get_user_input_for_value(key):
  """Gets user input for a value."""
  value = input("Enter a value for the key {}: ".format(key))
  return value

def add_key_value_to_library(library, key, value):
  """Adds a key-value pair to the library."""
  library[key] = value

def print_library(library):
  """Prints the library."""
  for key, value in library.items():
    print("{}: {}".format(key, value))

def main():
  """Main function."""

  # Create the library file if it doesn't exist.
  create_library_file_if_not_exists()

  # Load the library from a JSON file.
  library = load_library("output/library.json")

  # Get user input for a key.
  key = get_user_input()

  # Check the library for the key.
  if check_library_for_key(library, key):
    # If the key is in the library, print the key and value.
    value = library[key]
    print("{}: {}".format(key, value))
  else:
    # If the key is not in the library, get user input for a value and add the key-value pair to the library.
    value = get_user_input_for_value(key)
    add_key_value_to_library(library, key, value)

  # Save the library to a JSON file.
  save_library(library, "output/library.json")
  print("Saved to output/library.json")

if __name__ == "__main__":
  main()