import ctypes
import sys

from PySide6.QtCore import QDir
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pslipstream.config import Directories, config
from pslipstream.gui.main_window import MainWindow
from pslipstream.gui.workers import WORKER_THREAD


def start() -> None:
    """Start the GUI and Qt execution loop."""
    if sys.platform == "win32":
        # https://stackoverflow.com/a/1552105/13183782
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"com.rlaphoenix.slipstream")

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setStyleSheet((Directories.static / "style.qss").read_text("utf8"))
    app.setWindowIcon(QIcon(str(Directories.static / "img/icon.ico")))
    app.aboutToQuit.connect(config.save)
    app.aboutToQuit.connect(WORKER_THREAD.quit)
    QDir.setCurrent(str(Directories.root))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
