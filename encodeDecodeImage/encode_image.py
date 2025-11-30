# encode image

from PIL import Image
# import binascii

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
            pixel = list(pixels[i, j])  # type: ignore[assignment]
            for k in range(3):  # RGB
                if data_index < len(binary):
                    pixel[k] = pixel[k] & ~1 | int(binary[data_index])  # type: ignore[assignment]
                    data_index += 1
            pixels[i, j] = tuple(pixel)  # type: ignore[assignment]
    
    img.save('encoded_image.png')
    return 'encoded_image.png'

# Usage
# encoded_file = encode_image('original_image.png', 'Hello, this is a hidden message!')
encoded_file2 = encode_image('original_image.png', 'Duis ac molestie neque. Praesent id ex nec ex rutrum interdum. Donec in interdum arcu, a lobortis ligula. Nam eu metus quis elit feugiat convallis ac sit amet nibh. Sed quam ipsum, commodo eu nisl ac, viverra vestibulum turpis. Maecenas fringilla non felis sed ultricies. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc tincidunt vehicula dui sit amet sollicitudin. Aenean a eros interdum, scelerisque sapien eu, eleifend magna. Suspendisse luctus a dolor commodo tempus. Proin pellentesque iaculis neque at viverra. Ut vitae felis augue. Curabitur ut urna sit amet nunc eleifend pellentesque a id mi. Donec quis convallis leo, et ultricies metus. Ut dapibus risus id leo pharetra, vitae aliquam mauris interdum.\n\nQuisque auctor orci eget nisi facilisis, non egestas arcu eleifend. Nunc lobortis nec enim sed euismod. Praesent quis scelerisque orci. In at lacus arcu. Vestibulum sed accumsan ex, a blandit magna. Nullam et enim vitae lorem blandit condimentum. Donec pretium urna at ligula viverra, a rhoncus nunc accumsan. Donec at consectetur erat. Ut semper turpis et eros cursus sollicitudin. Integer eu tellus tincidunt, placerat felis et, lobortis magna. Maecenas commodo a dolor sed aliquet.\n\nNulla in dictum lectus, non suscipit lectus. Sed orci turpis, porttitor ac orci ac, aliquam mollis metus. Mauris quis urna a leo suscipit efficitur. Maecenas ut justo at arcu dapibus efficitur. In commodo, dui at dignissim ornare, risus sapien sodales orci, sit amet blandit odio augue et justo. Maecenas aliquam ante iaculis lectus auctor, ut scelerisque libero volutpat. Suspendisse venenatis urna sit amet consectetur sollicitudin. Etiam lacinia orci tortor, sed efficitur neque malesuada vel. Suspendisse porttitor feugiat purus a hendrerit. Nullam cursus imperdiet mi at pharetra. Nam cursus pharetra lorem, et aliquam diam lobortis quis.\n\nDonec eu ultricies purus. Fusce nec turpis at mauris posuere semper. Fusce mattis ultricies tortor sed dapibus. Donec sit amet venenatis dui, nec convallis odio. Mauris sit amet nunc fermentum, dignissim eros et, pellentesque augue. Etiam varius tellus a augue aliquet, non aliquam odio volutpat. Curabitur vel tristique purus. Quisque commodo sed orci sit amet lobortis. Mauris id rutrum tellus. Cras maximus, sapien et ultrices vulputate, dui mi pellentesque turpis, eu sodales justo nunc quis eros.')
print(f"Encoded image saved as {encoded_file2}")
