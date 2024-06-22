## Write sample python code that hides text in imagery

Here’s a simple example of how to encode and decode hidden data within an image using Python. This example will use the Python Imaging Library (PIL), part of the `Pillow` package, and basic manipulation of the least significant bit (LSB) of the pixel data to hide text data within an image. This is a rudimentary form of steganography.

### Installation Requirement

You will need the `Pillow` library to run this code. Install it using pip if you don't have it:

```bash
pip install Pillow
```

### Python Code: Encoding Text into an Image

```python
from PIL import Image
import binascii

def text_to_bin(text):
    """Convert text to binary."""
    binary = bin(int.from_bytes(text.encode(), 'big'))
    return binary[2:]

def encode_image(img_path, secret_message):
    """Encode text data into an image."""
    img = Image.open(img_path)
    binary = text_to_bin(secret_message) + '1111111111111110'  # Delimiter to indicate end of message
    pixels = img.load()
    
    data_index = 0
    for i in range(img.size[0]):
        if data_index >= len(binary):
            break
        for j in range(img.size[1]):
            if data_index >= len(binary):
                break
            pixel = list(pixels[i, j])
            for k in range(3):  # RGB
                if data_index < len(binary):
                    pixel[k] = pixel[k] & ~1 | int(binary[data_index])
                    data_index += 1
            pixels[i, j] = tuple(pixel)
    
    img.save('encoded_image.png')
    return 'encoded_image.png'

# Usage
encoded_file = encode_image('original_image.png', 'Hello, this is a hidden message!')
print(f"Encoded image saved as {encoded_file}")
```

### Python Code: Decoding Data from an Image

```python
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
```

### Explanation
- **Encoding**: The code converts the text message into a binary string and then modifies the least significant bit of each color component (RGB) of each pixel to encode the binary data. It uses a special binary sequence `1111111111111110` as a delimiter to mark the end of the text.
- **Decoding**: It reads the image, checks each pixel's color components for the modified LSBs, reconstructs the binary string, and checks for the delimiter. If found, it converts the binary string back to text.

Remember, this example is quite basic and primarily for educational purposes. Real-world applications would need more sophisticated methods for robustness and security.

---

# Create python code that creates a simple image of a colored circle

Here's a Python script that uses the `Pillow` library to create a simple image featuring a colored circle. This script will generate a PNG image with a blue circle on a white background. 

### Python Code to Create an Image with a Colored Circle

First, ensure you have the `Pillow` library installed. If not, you can install it using pip:

```bash
pip install Pillow
```

Now, here's the Python code to create the image:

```python
from PIL import Image, ImageDraw

def create_circle_image(output_path):
    # Create a new white image
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)

    # Define circle parameters
    center = (100, 100)
    radius = 50
    color = 'blue'

    # Draw the circle
    draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], fill=color)

    # Save the image
    img.save(output_path)
    return output_path

# Usage
image_path = create_circle_image('circle_image.png')
print(f"Circle image saved as {image_path}")
```

### Explanation

- **Image Creation**: The image is initialized with a white background using a size of 200x200 pixels.
- **Drawing**: The `ImageDraw` module is used to draw shapes on the image. Here, an ellipse is drawn that fits perfectly into a bounding box defined by the center and radius, resulting in a circle.
- **Saving**: The resulting image is saved to a file named `circle_image.png`.

This script will generate a simple yet visually clear image of a blue circle on a white background, which you can find in the specified directory.