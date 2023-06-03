from PIL import Image
import io


def convert_to_webp_for_avatar(image_data: bytes) -> bytes:
    result_io = io.BytesIO()
    image = Image.open(io.BytesIO(image_data))
    image.resize((256, 256))
    image.save(result_io, format="webp")
    return result_io.getvalue()
