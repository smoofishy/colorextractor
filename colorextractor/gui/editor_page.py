from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QSplitter, QVBoxLayout, QWidget

from ..extractor import extract_colors
from .color_panel import ColorPanel
from .image_view import ImageView
from .project import Project
from .system import reveal_in_file_manager


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
        try:
            self.image_view.set_image(project.path)
        except OSError as exc:
            self.statusMessage.emit(f"Could not open image: {exc}", 4000)
            return False

        self._image_path = project.path
        self.title_edit.setText(project.title)
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

    def _recompute(self):
        if not self._image_path:
            return
        settings = self.color_panel.get_settings()
        try:
            results = extract_colors(
                self._image_path,
                num_colors=settings["num_colors"],
                top_n=settings["top_n"],
                group_similar=settings["group_similar"],
            )
        except (FileNotFoundError, ValueError) as exc:
            self.statusMessage.emit(str(exc), 4000)
            return
        self.color_panel.set_colors(results)
