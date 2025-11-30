# decode image

from PIL import Image

# Same delimiter used in encode_image.py to mark the end of the message
DELIMITER = "1111111111111110"

def bin_to_text(binary: str) -> str:
    """Convert a binary string to text."""
    if not binary:
        return ""
    n = int(binary, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, "big").decode()


def decode_image(img_path: str) -> str:
    """
    Decode hidden text data from an image created by encode_image.py.

    The function:
    - Opens the image and converts it to RGB.
    - Reads the least significant bit from each RGB component in scanline order.
    - Stops when the delimiter is found.
    - Returns the decoded string, or 'No hidden message found' if the delimiter
      is never encountered.
    """
    img = Image.open(img_path).convert("RGB")
    pixels = img.load()

    binary = []

    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]  # type: ignore[assignment]
            for component in (r, g, b):
                binary.append(str(component & 1))
                # Only check for delimiter when we have at least its length
                if len(binary) >= len(DELIMITER):
                    # Check the trailing bits for delimiter
                    if "".join(binary[-len(DELIMITER) :]) == DELIMITER:
                        # Strip the delimiter bits off
                        message_bits = "".join(binary[:-len(DELIMITER)])
                        return bin_to_text(message_bits)

    return "No hidden message found"


if __name__ == "__main__":
    decoded_message = decode_image("encoded_image.png")
    print(f"Decoded message: {decoded_message}")
