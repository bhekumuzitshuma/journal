"""Image-channel fingerprint extraction."""

from pathlib import Path
from typing import Any


def jpeg_fingerprint(path: str | Path) -> dict[str, Any]:
    """Extract dimensions, size, JPEG tables, subsampling, and EXIF presence."""
    from PIL import Image, JpegImagePlugin

    image_path = Path(path)
    with Image.open(image_path) as image:
        quantization = getattr(image, "quantization", None)
        size = image_path.stat().st_size
        pixels = image.width * image.height
        return {
            "file": image_path.name,
            "width": image.width,
            "height": image.height,
            "bytes": size,
            "bpp": size * 8 / pixels if pixels else 0.0,
            "q_lum": list(quantization[0]) if quantization and 0 in quantization else None,
            "q_chr": list(quantization[1]) if quantization and 1 in quantization else None,
            "subsampling": JpegImagePlugin.get_sampling(image),
            "has_exif": bool(image.getexif()),
        }
