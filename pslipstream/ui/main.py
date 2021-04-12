import logging
import os
import subprocess

import pythoncom
import wmi
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QPushButton
from pycdlib import PyCdlib

from pslipstream import cfg
from pslipstream.dvd import Dvd


class Worker(QtCore.QObject):
    # input signals
    device = QtCore.Signal(dict)
    # output signals
    finished = QtCore.Signal(int)
    scanned_devices = QtCore.Signal(list)
    dvd = QtCore.Signal(Dvd)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def scan_devices(self):
        if cfg.windows:
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
            return
        if cfg.linux:
            lsscsi = subprocess.check_output(["lsscsi"]).decode().splitlines()
            lsscsi = [x[9:].strip() for x in lsscsi]
            lsscsi = [[x for x in scsi.split(" ") if x] for scsi in lsscsi]
            lsscsi = [x for x in lsscsi if x[0] not in ["disk"]]
            self.scanned_devices.emit([{
                "type": scsi[0],
                "make": scsi[1],
                "model": " ".join([scsi[2]] if len(scsi) == 5 else scsi[2:(len(scsi) - 2)]),
                "fwver": scsi[-2],
                "loc": scsi[-1],
                "volid": self.get_volume_id(scsi[-1])
            } for scsi in lsscsi])
            self.finished.emit(len(lsscsi))
            return

    @staticmethod
    def get_volume_id(device: str):
        """Get the Volume Identifier for a device."""
        log = logging.getLogger("cdlib")
        log.info("Getting Volume ID for {device}")
        cdlib = PyCdlib()
        try:
            cdlib.open(device, "rb")
        except OSError as e:
            # noinspection SpellCheckingInspection
            if "[Errno 123]" in str(e):
                # no disc inserted
                log.info(f"Device {device} has no disc inserted.")
                return None
            # noinspection SpellCheckingInspection
            if "[Errno 5]" in str(e):
                # Input/output error
                log.error(f"Device {device} had an I/O error.")
                return "! Error occurred reading disc..."
            raise
        volume_id = cdlib.pvds[0].volume_identifier.decode().strip()
        log.info(f"Device {device} has disc labeled \"{volume_id}\".")
        return volume_id

    def load_device(self, device: dict):
        dvd = Dvd()  # TODO: assumes disc is a DVD
        dvd.open(device["loc"])
        self.dvd.emit(dvd)
        self.finished.emit(0)


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

        def add_device_buttons(devices):
            device_list = self.widget.deviceListDevices_2.layout()
            for device in devices:
                button = QPushButton("{volume}\n{make} - {model}".format(
                    volume=device["volid"] or "No disc inserted...",
                    make=device["make"],
                    model=device["model"]
                ))
                button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                button.clicked.connect(lambda: self.load_device(device))
                if not device["volid"]:
                    button.setEnabled(False)
                device_list.insertWidget(0, button)

        self.worker.scanned_devices.connect(add_device_buttons)
        self.worker.finished.connect(lambda n: self.widget.statusbar.showMessage(f"Found {n} devices"))

        self.thread.start()

    def load_device(self, device: dict):
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.worker.device.connect(self.worker.load_device)

        self.thread.started.connect(lambda: self.widget.statusbar.showMessage(
            "Loading device %s - %s..." % (device["make"], device["model"])
        ))
        self.thread.started.connect(lambda: self.worker.device.emit(device))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def get_dvd(dvd: Dvd):
            print(dvd)

        self.worker.dvd.connect(get_dvd)

        self.worker.finished.connect(lambda: self.widget.backupButton.show())
        self.worker.finished.connect(lambda: self.widget.discInfoFrame.show())

        self.widget.backupButton.clicked.connect(lambda: self.backup_disc(device))

        self.thread.start()

    def backup_disc(self, device: dict):
        self.widget.statusbar.showMessage(
            "Backing up {volume} ({make} - {model})...".format(
                volume=device["volid"],
                make=device["make"],
                model=device["model"]
            )
        )
        self.widget.progressBar.show()
