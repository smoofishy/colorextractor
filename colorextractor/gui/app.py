import sys

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Color Extractor")
    # Thumbnail decoding and color extraction run on background threads;
    # wait for them to finish before the window (and the Qt objects whose
    # signals they report back through) gets torn down on quit.
    app.aboutToQuit.connect(lambda: QThreadPool.globalInstance().waitForDone())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
