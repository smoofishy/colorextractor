from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}

FILE_DIALOG_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.tif)"


def first_image_path(mime_data):
    """Return the path of the first dropped file that looks like an image, or None."""
    if not mime_data.hasUrls():
        return None
    for url in mime_data.urls():
        path = url.toLocalFile()
        if path and Path(path).suffix.lower() in IMAGE_EXTENSIONS:
            return path
    return None
