from PIL import Image
import io

def compress_image(image_file, quality=60):
    """
    Compress image and return bytes
    """
    img = Image.open(image_file)

    # Convert PNG → RGB (JPEG doesn't support alpha)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_pdf(file):
    if not file.content_type == "application/pdf":
        raise ValueError("Only PDF files are allowed")
    if file.size > MAX_FILE_SIZE:
        raise ValueError("PDF too large (max 10MB)")


def validate_image(file):
    if not file.content_type.startswith("image/"):
        raise ValueError("Only image files are allowed")
    if file.size > MAX_FILE_SIZE:
        raise ValueError("Image too large (max 10MB)")
