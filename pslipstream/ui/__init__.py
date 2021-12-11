import logging

import sys
from PySide2.QtCore import QDir, Qt, QFile
from PySide2.QtUiTools import QUiLoader

from pslipstream.config import Directories


class BaseWindow:
    def __init__(self, name: str, flag=Qt.Window) -> None:
        ui_file = QFile(str(Directories.root / "ui" / f"{name}.ui"))
        loader = QUiLoader()
        loader.setWorkingDirectory(QDir(str(Directories.root)))

        try:
            if not ui_file.open(QFile.ReadOnly):
                print("Cannot open UI file %s.ui, %s", name, ui_file.errorString())
                sys.exit(-1)
            self.window = loader.load(ui_file)
            if not self.window:
                print("Failed to load Ui Window for %s.ui, %s", name, loader.errorString())
                sys.exit(-1)
        finally:
            ui_file.close()

        self.window.setWindowFlags(flag)
        self.log = logging.getLogger(name)

    def show(self) -> None:
        self.window.show()
