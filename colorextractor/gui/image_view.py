from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea

from .image_io import load_pixmap
from .utils import first_image_path


class ImageView(QScrollArea):
    """The big center canvas that displays the selected image.

    Defaults to scaling the image to fit the viewport; once the user zooms
    in past that, the image is shown at its zoomed size and can be panned
    via the scrollbars.
    """

    MIN_ZOOM = 0.1
    MAX_ZOOM = 8.0
    ZOOM_STEP = 1.25

    imageDropped = Signal(str)
    zoomChanged = Signal(float)  # 1.0 == actual size

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("imageCanvas")
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

        self._canvas = QLabel()
        self._canvas.setAlignment(Qt.AlignCenter)
        self._canvas.setStyleSheet("background-color: #1e1e1e;")
        self.setWidget(self._canvas)
        self.viewport().setStyleSheet("background-color: #1e1e1e;")
        self.viewport().installEventFilter(self)

        self._original_pixmap = None
        self._zoom = None  # None means "fit to window"

    def set_image(self, path):
        self._original_pixmap = load_pixmap(path)
        self._zoom = None
        self._render()

    def zoom_in(self):
        self._zoom_at(self._effective_zoom() * self.ZOOM_STEP)

    def zoom_out(self):
        self._zoom_at(self._effective_zoom() / self.ZOOM_STEP)

    def zoom_to_fit(self):
        self._zoom = None
        self._render()

    def _zoom_at(self, new_zoom, viewport_pos=None):
        """Zoom to `new_zoom`, keeping the image point under `viewport_pos`
        (viewport-local coordinates) stationary on screen. Defaults to the
        viewport center when no position is given (e.g. toolbar buttons)."""
        if viewport_pos is None:
            viewport_pos = self.viewport().rect().center()

        if self._original_pixmap and not self._original_pixmap.isNull() and self._canvas.width() and self._canvas.height():
            content_pos = self._canvas.mapFrom(self.viewport(), viewport_pos)
            frac_x = content_pos.x() / self._canvas.width()
            frac_y = content_pos.y() / self._canvas.height()
        else:
            frac_x = frac_y = 0.5

        self._zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, new_zoom))
        self._render()

        new_w = self._canvas.width()
        new_h = self._canvas.height()
        self.horizontalScrollBar().setValue(round(frac_x * new_w - viewport_pos.x()))
        self.verticalScrollBar().setValue(round(frac_y * new_h - viewport_pos.y()))

    def _fit_zoom(self):
        if not self._original_pixmap or self._original_pixmap.isNull():
            return 1.0
        size = self._original_pixmap.size()
        viewport = self.viewport().size()
        if size.width() <= 0 or size.height() <= 0 or viewport.width() <= 0 or viewport.height() <= 0:
            return 1.0
        return min(viewport.width() / size.width(), viewport.height() / size.height())

    def _effective_zoom(self):
        return self._zoom if self._zoom is not None else self._fit_zoom()

    def _render(self):
        if not self._original_pixmap or self._original_pixmap.isNull():
            return
        zoom = self._effective_zoom()
        size = self._original_pixmap.size()
        target_w = max(1, round(size.width() * zoom))
        target_h = max(1, round(size.height() * zoom))
        scaled = self._original_pixmap.scaled(
            target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._canvas.setPixmap(scaled)
        self._canvas.resize(scaled.size())
        self.zoomChanged.emit(zoom)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._zoom is None:
            self._render()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta != 0:
                factor = self.ZOOM_STEP if delta > 0 else (1 / self.ZOOM_STEP)
                pos = self.viewport().mapFromParent(event.position().toPoint())
                self._zoom_at(self._effective_zoom() * factor, pos)
            event.accept()
        else:
            super().wheelEvent(event)

    def eventFilter(self, obj, event):
        if (
            obj is self.viewport()
            and event.type() == QEvent.NativeGesture
            and event.gestureType() == Qt.ZoomNativeGesture
        ):
            pos = event.position().toPoint()
            self._zoom_at(self._effective_zoom() * (1 + event.value()), pos)
            return True
        return super().eventFilter(obj, event)

    def dragEnterEvent(self, event):
        if first_image_path(event.mimeData()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = first_image_path(event.mimeData())
        if path:
            self.imageDropped.emit(path)
