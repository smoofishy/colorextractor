from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QSplitter, QVBoxLayout, QWidget

from ..extractor import extract_colors
from .color_panel import ColorPanel
from .image_io import load_pixmap
from .image_view import ImageView
from .project import Project
from .system import reveal_in_file_manager
from .workers import CallableThread


class EditorPage(QWidget):
    """Main editing view: big image canvas on the left, color list on the right."""

    statusMessage = Signal(str, int)
    backRequested = Signal()
    openRequested = Signal()
    imageOpenRequested = Signal(str)
    titleChanged = Signal(str, str)  # path, new title

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path = None
        self._thread_pool = QThreadPool.globalInstance()
        self._image_request_id = 0
        self._color_request_id = 0
        self._image_worker = None
        self._color_worker = None

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        self.image_view = ImageView()
        self.image_view.imageDropped.connect(self.imageOpenRequested)

        self.color_panel = ColorPanel()
        self.color_panel.settingsChanged.connect(self._recompute)
        self.color_panel.colorCopied.connect(
            lambda hex_code: self.statusMessage.emit(f"Copied {hex_code} to clipboard", 2000)
        )

        splitter.addWidget(self.image_view)
        splitter.addWidget(self.color_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([800, 320])

        outer_layout.addWidget(self._build_toolbar())
        outer_layout.addWidget(splitter, 1)

        self.image_view.zoomChanged.connect(self._on_zoom_changed)

    def _build_toolbar(self):
        toolbar = QWidget()
        toolbar.setObjectName("editorToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        back_button = QPushButton("‹ Projects")
        back_button.clicked.connect(self.backRequested)

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("titleEdit")
        self.title_edit.setFixedWidth(240)
        self.title_edit.editingFinished.connect(self._on_title_edited)

        zoom_out_button = QPushButton("–")
        zoom_out_button.clicked.connect(self.image_view.zoom_out)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(44)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")

        zoom_in_button = QPushButton("+")
        zoom_in_button.clicked.connect(self.image_view.zoom_in)

        fit_button = QPushButton("Fit")
        fit_button.clicked.connect(self.image_view.zoom_to_fit)

        reveal_button = QPushButton("Open in Finder")
        reveal_button.clicked.connect(self._reveal_in_finder)

        open_button = QPushButton("Add Another")
        open_button.clicked.connect(self.openRequested)

        layout.addWidget(back_button)
        layout.addWidget(self.title_edit)
        layout.addStretch(1)
        layout.addWidget(zoom_out_button)
        layout.addWidget(self.zoom_label)
        layout.addWidget(zoom_in_button)
        layout.addWidget(fit_button)
        layout.addSpacing(12)
        layout.addWidget(reveal_button)
        layout.addWidget(open_button)

        return toolbar

    def _reveal_in_finder(self):
        if self._image_path:
            reveal_in_file_manager(self._image_path)

    def _on_zoom_changed(self, zoom):
        self.zoom_label.setText(f"{zoom * 100:.0f}%")

    def load_image(self, project: Project):
        """Switch to this image immediately - the (possibly slow) decode
        and color analysis both run in the background so the editor is
        never blank-screened waiting on a big photo."""
        self._image_path = project.path
        self.title_edit.setText(project.title)
        self.image_view.clear("Loading image…")
        self._start_image_load(project.path)
        self._recompute()
        return True

    def current_path(self):
        return self._image_path

    def set_title(self, title):
        self.title_edit.setText(title)

    def _on_title_edited(self):
        if not self._image_path:
            return
        new_title = self.title_edit.text().strip()
        if not new_title:
            new_title = Project.from_path(self._image_path).title
            self.title_edit.setText(new_title)
        self.titleChanged.emit(self._image_path, new_title)

    def _start_image_load(self, path):
        self._image_request_id += 1
        request_id = self._image_request_id
        worker = CallableThread(lambda: load_pixmap(path))
        worker.succeeded.connect(lambda pixmap: self._on_image_loaded(request_id, pixmap))
        worker.failed.connect(lambda message: self._on_image_load_failed(request_id, message))
        self._image_worker = worker
        self._thread_pool.start(worker)

    def _on_image_loaded(self, request_id, pixmap):
        if request_id != self._image_request_id:
            return  # a newer image was opened before this one finished decoding
        self.image_view.set_pixmap(pixmap)

    def _on_image_load_failed(self, request_id, message):
        if request_id != self._image_request_id:
            return
        self.image_view.clear("Could not load image")
        self.statusMessage.emit(f"Could not open image: {message}", 4000)

    def _recompute(self):
        if not self._image_path:
            return
        path = self._image_path
        settings = self.color_panel.get_settings()
        self.color_panel.set_loading()

        self._color_request_id += 1
        request_id = self._color_request_id
        worker = CallableThread(
            lambda: extract_colors(
                path,
                num_colors=settings["num_colors"],
                top_n=settings["top_n"],
                group_similar=settings["group_similar"],
            )
        )
        worker.succeeded.connect(lambda results: self._on_colors_ready(request_id, results))
        worker.failed.connect(lambda message: self._on_colors_failed(request_id, message))
        self._color_worker = worker
        self._thread_pool.start(worker)

    def _on_colors_ready(self, request_id, results):
        if request_id != self._color_request_id:
            return  # settings changed again (or a new image loaded) before this finished
        self.color_panel.set_colors(results)

    def _on_colors_failed(self, request_id, message):
        if request_id != self._color_request_id:
            return
        self.color_panel.set_colors([])
        self.statusMessage.emit(message, 4000)
