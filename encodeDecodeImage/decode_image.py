# decode image

from PIL import Image

def bin_to_text(binary):
    """Convert binary code to text."""
    n = int(binary, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()

def decode_image(img_path):
    """Decode hidden text data from an image."""
    img = Image.open(img_path)
    pixels = img.load()
    
    binary = ''
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixel = pixels[i, j]
            for k in range(3):  # RGB
                binary += str(pixel[k] & 1)
                if binary.endswith('1111111111111110'):  # Check for the delimiter
                    return bin_to_text(binary[:-16])
    
    return "No hidden message found"

# Usage
decoded_message = decode_image('encoded_image.png')
print(f"Decoded message: {decoded_message}")
