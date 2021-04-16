import logging
import math
import os
import subprocess
import sys

import pythoncom
import wmi
from PySide2 import QtCore, QtGui
from PySide2.QtGui import QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QPushButton, QTreeWidgetItem
from pycdlib import PyCdlib

from pslipstream import cfg
from pslipstream.dvd import Dvd


class Worker(QtCore.QObject):
    # input signals
    device = QtCore.Signal(dict)
    disc = QtCore.Signal(Dvd)
    # output signals
    error = QtCore.Signal(Exception)
    finished = QtCore.Signal(int)
    progress = QtCore.Signal(float)
    scanned_devices = QtCore.Signal(dict)
    dvd = QtCore.Signal(Dvd)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def scan_devices(self):
        if cfg.windows:
            # noinspection PyUnresolvedReferences
            pythoncom.CoInitialize()  # important!
            c = wmi.WMI()
            drives = c.Win32_CDROMDrive()
            for drive in drives:
                self.scanned_devices.emit({
                    # "type": ?
                    "make": drive.name.split(" ")[0],
                    "model": drive.name.split(" ")[1],
                    "fwver": drive.mfrAssignedRevisionLevel,
                    "loc": drive.drive,  # e.g. "D:"
                    "volid": drive.volumeName
                })
            self.finished.emit(len(drives))
            return
        if cfg.linux:
            lsscsi = subprocess.check_output(["lsscsi"]).decode().splitlines()
            lsscsi = [x[9:].strip() for x in lsscsi]
            lsscsi = [[x for x in scsi.split(" ") if x] for scsi in lsscsi]
            lsscsi = [x for x in lsscsi if x[0] not in ["disk"]]
            for scsi in lsscsi:
                self.scanned_devices.emit({
                    "type": scsi[0],
                    "make": scsi[1],
                    "model": " ".join([scsi[2]] if len(scsi) == 5 else scsi[2:(len(scsi) - 2)]),
                    "fwver": scsi[-2],
                    "loc": scsi[-1],
                    "volid": self.get_volume_id(scsi[-1])
                })
            self.finished.emit(len(lsscsi))
            return
        self.error.emit(NotImplementedError("Device Scanning has not been implemented for %s." % sys.platform))

    @staticmethod
    def get_volume_id(device: str):
        """Get the Volume Identifier for a device."""
        log = logging.getLogger("cdlib")
        log.info("Getting Volume ID for %s" % device)
        cdlib = PyCdlib()
        try:
            cdlib.open(device, "rb")
        except OSError as e:
            # noinspection SpellCheckingInspection
            if "[Errno 123]" in str(e):
                # no disc inserted
                log.info("Device %s has no disc inserted." % device)
                return None
            # noinspection SpellCheckingInspection
            if "[Errno 5]" in str(e):
                # Input/output error
                log.error("Device %s had an I/O error." % device)
                return "! Error occurred reading disc..."
            raise
        volume_id = cdlib.pvds[0].volume_identifier.decode().strip()
        log.info('Device %s has disc labeled "%s".' % (device, volume_id))
        return volume_id

    def load_device(self, device: dict):
        try:
            pythoncom.CoInitialize()
            dvd = Dvd()  # TODO: assumes disc is a DVD
            dvd.open(device["loc"])
            self.dvd.emit(dvd)
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)

    def backup_disc(self, disc: Dvd):
        try:
            disc.create_backup(self.progress)
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)


class UI(QMainWindow):

    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        ui_loader = QUiLoader()
        ui_file = QtCore.QFile(os.path.join(os.path.dirname(__file__), cfg.static_dir / "form.ui"))
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
        """Gets list of disc readers and adds them to device list."""
        self.clear_device_list()

        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.widget.progressBar.hide()
            self.widget.backupButton.hide()
            self.widget.discInfoFrame.hide()
            self.widget.discInfoList.clear()
            self.widget.statusbar.showMessage("Scanning devices...")

        def on_finish(n: int):
            self.widget.statusbar.showMessage("Found %d devices" % n)

        def add_device_button(device: dict):
            device_list = self.widget.deviceListDevices_2.layout()
            button = QPushButton("{volume}\n{make} - {model}".format(
                volume=device["volid"] or "No disc inserted...",
                make=device["make"],
                model=device["model"]
            ))
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            button.clicked.connect(lambda: self.load_device(device))
            if not device["volid"]:
                button.setEnabled(False)
            device_list.insertWidget(device_list.count() - 1 if not device["volid"] else 0, button)

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.scanned_devices.connect(add_device_button)

        self.thread.started.connect(self.worker.scan_devices)
        self.thread.start()

    def load_device(self, device: dict):
        """
        Load device, get disc object, get disc information.
        Currently only supports DVD discs.
        """
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.widget.progressBar.hide()
            self.widget.backupButton.hide()
            self.widget.discInfoFrame.hide()
            self.widget.discInfoList.clear()
            self.widget.statusbar.showMessage("Loading device %s - %s..." % (device["make"], device["model"]))

        def on_finish(_: int):
            self.widget.backupButton.show()
            self.widget.discInfoFrame.show()
            self.widget.statusbar.showMessage("Loaded device %s - %s..." % (device["make"], device["model"]))

        def get_dvd(dvd: Dvd):
            self.widget.discInfoList.clear()
            disc_id = dvd.compute_crc_id()
            disc_id_tree = QTreeWidgetItem(["Disc ID", disc_id])
            self.widget.discInfoList.addTopLevelItem(disc_id_tree)

            pvd = dvd.get_primary_descriptor()
            pvd_tree = QTreeWidgetItem(["Primary Volume Descriptor"])
            for k, v in pvd.items():
                pvd_tree.addChild(QTreeWidgetItem([k, repr(v or "NULL")]))
            self.widget.discInfoList.addTopLevelItem(pvd_tree)

            self.widget.backupButton.clicked.connect(lambda: self.backup_disc(device, dvd))

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.dvd.connect(get_dvd)

        self.worker.device.connect(self.worker.load_device)
        self.thread.started.connect(lambda: self.worker.device.emit(device))
        self.thread.start()

    def backup_disc(self, device: dict, disc: Dvd):
        """Backup loaded disc to an ISO file."""
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.widget.progressBar.show()
            self.widget.backupButton.setEnabled(False)
            self.widget.statusbar.showMessage(
                "Backing up %s (%s - %s)..." % (device["volid"], device["make"], device["model"])
            )

        def on_progress(n: float):
            self.widget.progressBar.setValue(n)
            self.widget.backupButton.setText("Backing up... %d%%" % math.floor(n))

        def on_finish():
            self.widget.backupButton.setText("Backup")
            self.widget.statusbar.showMessage(
                "Backed up %s (%s - %s)..." % (device["volid"], device["make"], device["model"])
            )
            self.widget.backupButton.setEnabled(True)

        def on_error(e: Exception):
            print(e)

        self.thread.started.connect(manage_state)
        self.worker.progress.connect(on_progress)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)

        self.worker.disc.connect(self.worker.backup_disc)
        self.thread.started.connect(lambda: self.worker.disc.emit(disc))
        self.thread.start()
