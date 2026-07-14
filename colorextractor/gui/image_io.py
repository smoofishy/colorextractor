from PIL import Image as PILImage
from PIL import ImageOps
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


def load_pixmap(path) -> QPixmap:
    """Load an image file into a QPixmap via Pillow.

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


def _cover_crop(pixmap: QPixmap, size: int) -> QPixmap:
    """Scale to fill a size x size square, then center-crop the overflow."""
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = max(0, (scaled.width() - size) // 2)
    y = max(0, (scaled.height() - size) // 2)
    return scaled.copy(x, y, size, size)


def make_tile_icon(path, size: int) -> QIcon:
    """A square, cover-cropped thumbnail for a project-grid tile."""
    try:
        pixmap = load_pixmap(path)
    except OSError:
        return _broken_tile_icon(size)
    return QIcon(_cover_crop(pixmap, size))


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


def _broken_tile_icon(size: int) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#2b2b2b"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("#666666"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "?")
    painter.end()
    return QIcon(pixmap)
