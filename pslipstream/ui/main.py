import inspect
import os
from pathlib import Path

import pythoncom
import wmi
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QPushButton

from pslipstream import cfg


class Devices(QtCore.QObject):
    finished = QtCore.Signal()
    result = QtCore.Signal(list)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @QtCore.Slot(list)
    def getDevices(self):
        pythoncom.CoInitialize()  # important!
        c = wmi.WMI()
        drives = c.Win32_CDROMDrive()
        self.result.emit([{
            # "type": ?
            "make": x.name.split(" ")[0],
            "model": x.name.split(" ")[1],
            "fwver": x.mfrAssignedRevisionLevel,
            "loc": x.drive,  # e.g. "D:"
            "volid": x.volumeName
        } for x in drives])
        self.finished.emit()


class UI(QMainWindow):

    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        ui_loader = QUiLoader()
        ui_file = QtCore.QFile(os.path.join(os.path.dirname(__file__), "form.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = ui_loader.load(ui_file, parent)
        self.widget.setWindowFlags(QtCore.Qt.Window)
        ui_file.close()

        self.devices = []

        self.configure()

    def configure(self):
        self.widget.setWindowTitle("Slipstream")
        self.widget.log.append(inspect.cleandoc("""
        Slipstream  Copyright (C) 2021 PHOENiX
        This program comes with ABSOLUTELY NO WARRANTY.
        This is free software, and you are welcome to redistribute it
        under certain conditions; type 'pslipstream --license' for details.

        Slipstream v0.4.0
        The most informative Home-media backup solution.
        https://github.com/rlaPHOENiX/Slipstream
        """))

        self.widget.backupButton.hide()
        self.clear_device_list()  # clear example buttons

        self.widget.refreshIcon.clicked.connect(self.load_devices)
        self.widget.refreshIcon.setIcon(QPixmap(str(cfg.root_dir / "static" / "img" / "refresh.svg")))
        self.widget.discIcon.setIcon(QPixmap(str(cfg.root_dir / "static" / "img" / "music-disc-with-luster.svg")))
        self.widget.logIcon.setIcon(QPixmap(str(cfg.root_dir / "static" / "img" / "align.svg")))

    def show(self):
        self.widget.show()

    def clear_device_list(self):
        for device in self.widget.deviceListDevices_2.children():
            if isinstance(device, QPushButton):
                device.setParent(None)

    def load_device(self, device: dict):
        self.device = device
    def load_devices(self):
        self.clear_device_list()

        self.thread = QtCore.QThread()
        self.worker = Devices()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(lambda: self.widget.statusbar.showMessage("Loading devices..."))
        self.thread.started.connect(self.worker.getDevices)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        @QtCore.Slot(list)
        def add_device_buttons(devices):
            device_list = self.widget.deviceListDevices_2.layout()
            for device in devices:
                button = QPushButton("{volume}\n{make} - {model}".format(
                    volume=device["volid"],
                    make=device["make"],
                    model=device["model"]
                ))
                button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                button.clicked.connect(lambda: self.load_device(device))
                if not device["volid"]:
                    button.setEnabled(False)
                device_list.insertWidget(0, button)

        self.worker.result.connect(lambda devices: setattr(self, "devices", devices))
        self.worker.result.connect(add_device_buttons)

        self.thread.start()
        self.thread.finished.connect(lambda: self.widget.statusbar.showMessage(f"Loaded {len(self.devices)} devices"))
