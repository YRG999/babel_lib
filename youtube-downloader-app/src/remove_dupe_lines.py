import os

def remove_duplicate_lines(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        prev_line = None
        for line in infile:
            if line != prev_line:
                outfile.write(line)
            prev_line = line

# if __name__ == "__main__":
#     input_file = "Sam Hyde Show： Boomers [KtFvYqKcDpQ].en.txt"
#     output_file = "Sam Hyde Show： Boomers [KtFvYqKcDpQ].en.deduped.txt"
#     remove_duplicate_lines(input_file, output_file)
#     print(f"Deduplicated transcript saved to {output_file}")

def remove_all_duplicates(input_path, output_path):
    seen = set()
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line not in seen:
                outfile.write(line)
                seen.add(line)

if __name__ == "__main__":
    input_file = input("Enter the input file path: ")
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_deduped{ext}"
    remove_all_duplicates(input_file, output_file)
    print(f"Deduplicated transcript saved to {output_file}")