"""Dark theme stylesheet, styled after the panel-heavy look of apps like
Photoshop and Lightroom."""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #323232;
    color: #d4d4d4;
    font-family: -apple-system, "Helvetica Neue", "Segoe UI", sans-serif;
    font-size: 12px;
}

QMenuBar {
    background-color: #262626;
    border-bottom: 1px solid #1e1e1e;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background-color: #454545;
}
QMenu {
    background-color: #2b2b2b;
    border: 1px solid #1e1e1e;
}
QMenu::item {
    padding: 6px 24px;
}
QMenu::item:selected {
    background-color: #0f6fc5;
}

QSplitter::handle {
    background-color: #1e1e1e;
}
QSplitter::handle:horizontal {
    width: 1px;
}

#imageCanvas {
    background-color: #1e1e1e;
}

#editorToolbar {
    background-color: #262626;
    border-bottom: 1px solid #1e1e1e;
}

#colorPanel {
    background-color: #2b2b2b;
    border-left: 1px solid #1e1e1e;
}

QListWidget {
    background-color: #2b2b2b;
    border: none;
    outline: none;
}
QListWidget::item {
    border-bottom: 1px solid #262626;
}
QListWidget::item:hover {
    background-color: #383838;
}
QListWidget::item:selected {
    background-color: #0f6fc5;
}

QPushButton {
    background-color: #454545;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    padding: 6px 16px;
    color: #e0e0e0;
}
QPushButton:hover {
    background-color: #525252;
}
QPushButton:pressed {
    background-color: #0f6fc5;
}

QLineEdit {
    background-color: #262626;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    padding: 5px 10px;
    color: #d4d4d4;
}
QLineEdit:focus {
    border-color: #0f6fc5;
}

#titleEdit {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 3px 6px;
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 600;
}
#titleEdit:hover {
    background-color: #303030;
}
#titleEdit:focus {
    background-color: #1e1e1e;
    border-color: #0f6fc5;
}

QListWidget#projectGrid {
    background-color: transparent;
    border: none;
}
QListWidget#projectGrid::item {
    color: #cccccc;
    padding: 6px;
    border: none;
    border-radius: 6px;
}
QListWidget#projectGrid::item:hover {
    background-color: #3a3a3a;
}
QListWidget#projectGrid::item:selected {
    background-color: #0f6fc5;
    color: #ffffff;
}

QSpinBox {
    background-color: #262626;
    border: 1px solid #1e1e1e;
    border-radius: 3px;
    padding: 2px 4px;
    min-width: 50px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #262626;
}
QCheckBox::indicator:checked {
    background-color: #0f6fc5;
    border-color: #0f6fc5;
}

QStatusBar {
    background-color: #262626;
    color: #999999;
    border-top: 1px solid #1e1e1e;
}

QScrollBar:vertical {
    background: #2b2b2b;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #4a4a4a;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #5a5a5a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
