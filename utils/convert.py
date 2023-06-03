from PIL import Image
import io


def convert_to_webp_for_avatar(image_data: bytes) -> bytes:
    result_io = io.BytesIO()
    image = Image.open(io.BytesIO(image_data))
    image_width, image_height = image.size
    min_size = min(image.size)
    image = image.crop(
        (
            (image_width - min_size) // 2,
            (image_height - min_size) // 2,
            (image_width + min_size) // 2,
            (image_height + min_size) // 2,
        )
    )
    image = image.resize((256, 256))
    image.save(result_io, format="webp", optimize=True, quality=80)
    return result_io.getvalue()
