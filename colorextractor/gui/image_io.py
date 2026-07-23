from PIL import Image as PILImage
from PIL import ImageOps
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap


def load_pixmap(path) -> QPixmap:
    """Load an image file into a QPixmap via Pillow, at full resolution.

    Qt's own image plugins don't cover every format Pillow can read, so
    routing display through Pillow keeps the canvas in sync with what the
    color extractor is actually able to open. Also applies EXIF orientation
    so photos display right-side up.
    """
    with PILImage.open(path) as im:
        im = ImageOps.exif_transpose(im)
        im = im.convert("RGB")
        qimage = ImageQt(im)
        return QPixmap.fromImage(qimage.copy())


def load_thumbnail_qimage(path, size: int) -> QImage:
    """A square, cover-cropped thumbnail, decoded at reduced resolution.

    Returns a QImage rather than a QPixmap so this can safely run on a
    background thread (QPixmap is GUI-thread-only; QImage isn't). Uses
    Pillow's JPEG "draft" mode, which has the decoder itself scale down
    while decoding instead of decoding at full resolution and scaling
    afterwards - the difference that keeps large photos from stalling the
    welcome screen.
    """
    with PILImage.open(path) as im:
        im.draft("RGB", (size, size))
        im = ImageOps.exif_transpose(im)
        im = im.convert("RGB")
        im = ImageOps.fit(im, (size, size), PILImage.LANCZOS)
        return ImageQt(im).copy()


def plus_tile_icon(size: int) -> QIcon:
    """The '+' tile used for the 'Open Image' grid entry."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#3a3a3a"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size, size, 10, 10)

    pen = QPen(QColor("#999999"))
    pen.setWidth(3)
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    cx, cy, arm = size / 2, size / 2, size * 0.16
    painter.drawLine(int(cx - arm), int(cy), int(cx + arm), int(cy))
    painter.drawLine(int(cx), int(cy - arm), int(cx), int(cy + arm))
    painter.end()

    return QIcon(pixmap)


def placeholder_tile_icon(size: int) -> QIcon:
    """Neutral filler shown for a tile while its thumbnail loads in the background."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#2b2b2b"))
    return QIcon(pixmap)


def broken_tile_icon(size: int) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#2b2b2b"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("#666666"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "?")
    painter.end()
    return QIcon(pixmap)
