from PIL import Image
import io


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _peek_bytes(uploaded_file, size=8):
    """Read a few bytes and restore cursor so later code can read normally."""
    if not uploaded_file:
        return b""

    try:
        pos = uploaded_file.tell()
    except Exception:
        pos = None

    header = uploaded_file.read(size)

    try:
        uploaded_file.seek(0 if pos is None else pos)
    except Exception:
        pass

    return header or b""


def compress_image(image_file, quality=60):
    """
    Compress image and return bytes.
    """
    img = Image.open(image_file)

    # Convert PNG -> RGB (JPEG does not support alpha)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def validate_pdf(file):
    if not file:
        raise ValueError("PDF file is required")

    if file.size > MAX_FILE_SIZE:
        raise ValueError("PDF too large (max 10MB)")

    content_type = (getattr(file, "content_type", "") or "").lower()
    name = (getattr(file, "name", "") or "").lower()
    header = _peek_bytes(file, 5)

    # Accept if any strong PDF signal matches.
    has_pdf_type = content_type in {"application/pdf", "application/x-pdf"}
    has_pdf_name = name.endswith(".pdf")
    has_pdf_signature = header.startswith(b"%PDF-")

    if not (has_pdf_type or has_pdf_name or has_pdf_signature):
        raise ValueError("Only PDF files are allowed")


def validate_image(file):
    if not file:
        raise ValueError("Image file is required")

    if file.size > MAX_FILE_SIZE:
        raise ValueError("Image too large (max 10MB)")

    content_type = (getattr(file, "content_type", "") or "").lower()
    if content_type and content_type.startswith("image/"):
        return

    # Fallback validation when content-type is missing or generic.
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception:
        raise ValueError("Only image files are allowed")
