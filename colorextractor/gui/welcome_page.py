from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from .image_io import broken_tile_icon, load_thumbnail_qimage, placeholder_tile_icon, plus_tile_icon
from .utils import FILE_DIALOG_FILTER, first_image_path

TILE_SIZE = 170
OPEN_ITEM_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole
NAME_LIMIT = 20


def _short_name(name):
    return name if len(name) <= NAME_LIMIT else name[: NAME_LIMIT - 1] + "…"


class _ThumbnailSignals(QObject):
    ready = Signal(str, object)  # (path, QImage | None)


class _ThumbnailTask(QRunnable):
    """Decodes one tile's thumbnail off the GUI thread.

    Emits a QImage rather than a QIcon/QPixmap: QPixmap has GUI-thread
    affinity, so building it must happen back on the main thread.
    """

    def __init__(self, path, size, signals):
        super().__init__()
        self._path = path
        self._size = size
        self._signals = signals

    def run(self):
        try:
            qimage = load_thumbnail_qimage(self._path, self._size)
        except OSError:
            qimage = None
        self._signals.ready.emit(self._path, qimage)


class WelcomePage(QWidget):
    """Project-selector grid shown on launch: an 'Add Another' tile plus
    thumbnails of recently opened images."""

    imageSelected = Signal(str)
    projectRenamed = Signal(str, str)  # path, new title

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(16)
        layout.addLayout(self._build_top_bar())

        self.grid = QListWidget()
        self.grid.setObjectName("projectGrid")
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(TILE_SIZE, TILE_SIZE))
        self.grid.setGridSize(QSize(TILE_SIZE + 30, TILE_SIZE + 46))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setMovement(QListWidget.Static)
        self.grid.setUniformItemSizes(True)
        self.grid.setSpacing(12)
        self.grid.setFrameShape(QListWidget.NoFrame)
        self.grid.itemClicked.connect(self._on_item_clicked)
        self.grid.itemChanged.connect(self._on_item_edited)
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.grid, 1)

        self._add_open_tile()

        self._thumbnail_pool = QThreadPool.globalInstance()
        self._thumbnail_signals = _ThumbnailSignals()
        self._thumbnail_signals.ready.connect(self._on_thumbnail_ready)

    def _build_top_bar(self):
        row = QHBoxLayout()

        title = QLabel("Recents")
        title.setStyleSheet("font-size: 15px; font-weight: 600; color: #e0e0e0;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search")
        self.search_box.setFixedWidth(220)
        self.search_box.textChanged.connect(self._apply_filter)

        row.addWidget(title)
        row.addStretch(1)
        row.addWidget(self.search_box)
        return row

    def _add_open_tile(self):
        item = QListWidgetItem(plus_tile_icon(TILE_SIZE), "Add Another")
        item.setData(OPEN_ITEM_ROLE, True)
        item.setTextAlignment(Qt.AlignHCenter)
        self.grid.addItem(item)

    def set_recent(self, projects):
        """Populate the grid instantly with placeholder tiles, then decode
        each thumbnail on a background thread so opening the app never
        blocks on reading a pile of large photos off disk."""
        self.grid.blockSignals(True)
        while self.grid.count() > 1:
            self.grid.takeItem(1)
        placeholder = placeholder_tile_icon(TILE_SIZE)
        for project in projects:
            item = QListWidgetItem(placeholder, _short_name(project.title))
            item.setData(PATH_ROLE, project.path)
            item.setToolTip(project.path)
            item.setTextAlignment(Qt.AlignHCenter)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.grid.addItem(item)
        self.grid.blockSignals(False)
        self._apply_filter(self.search_box.text())

        for project in projects:
            self._thumbnail_pool.start(_ThumbnailTask(project.path, TILE_SIZE, self._thumbnail_signals))

    def _on_thumbnail_ready(self, path, qimage):
        item = self._find_item(path)
        if item is None:
            return
        icon = QIcon(QPixmap.fromImage(qimage)) if qimage is not None else broken_tile_icon(TILE_SIZE)
        self.grid.blockSignals(True)
        item.setIcon(icon)
        self.grid.blockSignals(False)

    def _find_item(self, path):
        for i in range(self.grid.count()):
            item = self.grid.item(i)
            if item.data(PATH_ROLE) == path:
                return item
        return None

    def _apply_filter(self, text):
        text = text.strip().lower()
        for i in range(self.grid.count()):
            item = self.grid.item(i)
            if item.data(OPEN_ITEM_ROLE):
                continue
            item.setHidden(bool(text) and text not in item.text().lower())

    def _on_item_clicked(self, item):
        if item.data(OPEN_ITEM_ROLE):
            self._browse()
            return
        path = item.data(PATH_ROLE)
        if path:
            self.imageSelected.emit(path)

    def _show_context_menu(self, pos):
        item = self.grid.itemAt(pos)
        if item is None or item.data(OPEN_ITEM_ROLE):
            return
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        action = menu.exec(self.grid.viewport().mapToGlobal(pos))
        if action is rename_action:
            self.grid.editItem(item)

    def _on_item_edited(self, item):
        if item.data(OPEN_ITEM_ROLE):
            return
        path = item.data(PATH_ROLE)
        new_title = item.text().strip()
        if path and new_title:
            self.projectRenamed.emit(path, new_title)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select an Image", "", FILE_DIALOG_FILTER)
        if path:
            self.imageSelected.emit(path)

    def dragEnterEvent(self, event):
        if first_image_path(event.mimeData()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = first_image_path(event.mimeData())
        if path:
            self.imageSelected.emit(path)
