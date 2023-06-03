from PIL import Image
import io


def convert_to_webp(image_data: bytes) -> bytes:
    result_io = io.BytesIO()
    image = Image.open(io.BytesIO(image_data))
    image.save(result_io, format="webp")
    return result_io.getvalue()
