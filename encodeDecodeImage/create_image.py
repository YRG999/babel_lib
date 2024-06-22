# create image

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
