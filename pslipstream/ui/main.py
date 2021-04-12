import os

import pythoncom
import wmi
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QPushButton

from pslipstream import cfg


class Worker(QtCore.QObject):
    finished = QtCore.Signal(int)
    scanned_devices = QtCore.Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @QtCore.Slot(list)
    def scan_devices(self):
        # noinspection PyUnresolvedReferences
        pythoncom.CoInitialize()  # important!
        c = wmi.WMI()
        drives = c.Win32_CDROMDrive()
        self.scanned_devices.emit([{
            # "type": ?
            "make": x.name.split(" ")[0],
            "model": x.name.split(" ")[1],
            "fwver": x.mfrAssignedRevisionLevel,
            "loc": x.drive,  # e.g. "D:"
            "volid": x.volumeName
        } for x in drives])
        self.finished.emit(len(drives))


class UI(QMainWindow):

    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        ui_loader = QUiLoader()
        ui_file = QtCore.QFile(os.path.join(os.path.dirname(__file__), "form.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)
        self.widget = ui_loader.load(ui_file, parent)
        self.widget.setWindowFlags(QtCore.Qt.Window)
        ui_file.close()

        self.thread = None
        self.worker = None

        self.device = None

        self.configure()

    def configure(self):
        self.widget.setWindowTitle("Slipstream")

        self.widget.backupButton.hide()
        self.widget.discInfoFrame.hide()
        self.widget.progressBar.hide()
        self.clear_device_list()  # clear example buttons

        self.widget.refreshIcon.clicked.connect(self.scan_devices)
        self.widget.refreshIcon.setIcon(QPixmap(str(cfg.root_dir / "static" / "img" / "refresh.svg")))
        self.widget.discIcon.setPixmap(QPixmap(str(cfg.root_dir / "static" / "img" / "music-disc-with-luster.svg")))
        self.widget.logIcon.setPixmap(QPixmap(str(cfg.root_dir / "static" / "img" / "align.svg")))
        self.widget.infoIcon.setPixmap(QPixmap(str(cfg.root_dir / "static" / "img" / "info-circle.svg")))

    def show(self):
        self.widget.show()

    def clear_device_list(self):
        for device in self.widget.deviceListDevices_2.children():
            if isinstance(device, QPushButton):
                # noinspection PyTypeChecker
                device.setParent(None)

    def scan_devices(self):
        self.clear_device_list()

        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(lambda: self.widget.statusbar.showMessage("Scanning devices..."))
        self.thread.started.connect(self.worker.scan_devices)
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

        self.worker.scanned_devices.connect(lambda devices: setattr(self, "devices", devices))
        self.worker.scanned_devices.connect(add_device_buttons)

        self.thread.start()
        self.thread.finished.connect(lambda n: self.widget.statusbar.showMessage(f"Found {n} devices"))

    def load_device(self, device: dict):
        self.device = device

        # TODO: load device, get info, add to disc info section

        self.widget.backupButton.clicked.connect(lambda: self.backup_disc(device))
        self.widget.backupButton.show()
        self.widget.discInfoFrame.show()

    def backup_disc(self, device: dict):
        self.widget.statusbar.showMessage(
            "Backing up {volume} ({make} - {model})...".format(
                volume=device["volid"],
                make=device["make"],
                model=device["model"]
            )
        )
        self.widget.progressBar.show()
