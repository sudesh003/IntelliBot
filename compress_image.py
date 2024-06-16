from PIL import Image
from io import BytesIO

def compress_image(image_bytes: bytes) -> bytes:
    # Convert bytes to PIL Image
    original_image = Image.open(BytesIO(image_bytes))

    # Perform image compression without changing the size
    compressed_image_bytes = BytesIO()
    original_image.save(compressed_image_bytes, format='JPEG', quality=20)

    return compressed_image_bytes.getvalue()
