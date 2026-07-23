from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QStackedWidget

from .editor_page import EditorPage
from .project import Project
from .storage import load_recent_projects, save_recent_projects
from .theme import DARK_STYLESHEET
from .utils import FILE_DIALOG_FILTER
from .welcome_page import WelcomePage


class MainWindow(QMainWindow):
    MAX_RECENT = 12

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Extractor")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

        self._recent_projects = load_recent_projects()

        self.welcome_page = WelcomePage()
        self.editor_page = EditorPage()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.welcome_page)
        self.stack.addWidget(self.editor_page)
        self.setCentralWidget(self.stack)

        self.welcome_page.set_recent(self._recent_projects)

        self.welcome_page.imageSelected.connect(self.open_image)
        self.welcome_page.projectRenamed.connect(self._on_project_renamed)
        self.editor_page.statusMessage.connect(self.statusBar().showMessage)
        self.editor_page.backRequested.connect(self._show_welcome)
        self.editor_page.openRequested.connect(self._browse_file)
        self.editor_page.imageOpenRequested.connect(self.open_image)
        self.editor_page.titleChanged.connect(self._on_project_renamed)

        self._build_menu()

    def _build_menu(self):
        menu = self.menuBar().addMenu("File")

        open_action = QAction("Open Image…", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._browse_file)
        menu.addAction(open_action)

        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self._show_welcome)
        menu.addAction(new_project_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        view_menu = self.menuBar().addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.editor_page.image_view.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.editor_page.image_view.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_fit_action = QAction("Zoom to Fit", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(self.editor_page.image_view.zoom_to_fit)
        view_menu.addAction(zoom_fit_action)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select an Image", "", FILE_DIALOG_FILTER)
        if path:
            self.open_image(path)

    def _show_welcome(self):
        self.stack.setCurrentWidget(self.welcome_page)

    def open_image(self, path):
        project = self._find_project(path) or Project.from_path(path)
        if not self.editor_page.load_image(project):
            return
        self._remember_recent(project)
        self.stack.setCurrentWidget(self.editor_page)

    def _find_project(self, path):
        return next((p for p in self._recent_projects if p.path == path), None)

    def _remember_recent(self, project):
        existing = self._find_project(project.path)
        if existing:
            self._recent_projects.remove(existing)
        self._recent_projects.insert(0, project)
        del self._recent_projects[self.MAX_RECENT:]
        self.welcome_page.set_recent(self._recent_projects)
        save_recent_projects(self._recent_projects)

    def _on_project_renamed(self, path, new_title):
        project = self._find_project(path)
        if not project:
            return
        project.title = new_title
        self.welcome_page.set_recent(self._recent_projects)
        save_recent_projects(self._recent_projects)
        if self.editor_page.current_path() == path:
            self.editor_page.set_title(new_title)
