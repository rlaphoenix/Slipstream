import logging

from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader

from pslipstream.config import Directories


class BaseWindow:
    def __init__(self, name: str, flag=QtCore.Qt.Window) -> None:
        loader = QUiLoader()
        loader.setWorkingDirectory(QtCore.QDir(str(Directories.root)))
        ui_file = QtCore.QFile(str(Directories.root / "ui" / f"{name}.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)

        self.window = loader.load(ui_file)
        self.window.setWindowFlags(flag)
        ui_file.close()

        self.log = logging.getLogger(name)

    def show(self) -> None:
        self.window.show()
