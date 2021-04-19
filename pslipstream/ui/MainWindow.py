import logging
import math
import struct
import sys

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMessageBox

from pslipstream import cfg
from pslipstream.dvd import Dvd
from pslipstream.ui.DeviceWorker import DeviceWorker


class MainWindow:

    def __init__(self):
        self.ui = self.open()
        self.log = logging.getLogger("GUI")

        self.thread = None
        self.worker = None

        self.setup_ui()
        self.connect_io()

    def show(self):
        self.ui.show()

    def setup_ui(self):
        self.clear_device_list()  # clear example buttons

        self.ui.backupButton.setEnabled(False)
        self.ui.backupButton.hide()
        self.ui.discInfoFrame.hide()
        self.ui.progressBar.hide()

    def connect_io(self):
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.refreshIcon.clicked.connect(self.scan_devices)

    def about(self):
        QMessageBox.about(
            self.ui,
            "About %s" % cfg.title,
            ("%s v%s [%s]" % (
                cfg.title,
                cfg.version,
                ",".join(map(str, filter(None, [
                    sys.platform,
                    "%dbit" % (8 * struct.calcsize("P")),
                    cfg.py_version,
                    [None, "frozen"][cfg.frozen]
                ])))
            )) +
            ("<p>%s</p>" % cfg.copyright_line) +
            ("<p>{0}<br/><a href='{1}' style='color:white'>{1}</a></p>".format(cfg.description, cfg.url))
        )

    def clear_device_list(self):
        for device in self.ui.deviceListDevices_2.children():
            if isinstance(device, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                device.setParent(None)

    def scan_devices(self):
        """Gets list of disc readers and adds them to device list."""
        self.clear_device_list()

        self.thread = QtCore.QThread()
        self.worker = DeviceWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.ui.refreshIcon.setEnabled(False)
            self.ui.progressBar.hide()
            self.ui.backupButton.hide()
            self.ui.discInfoFrame.hide()
            self.ui.discInfoList.clear()
            self.ui.statusbar.showMessage("Scanning devices...")

        def on_finish(n: int):
            self.ui.refreshIcon.setEnabled(True)
            self.ui.statusbar.showMessage("Found %d devices" % n)

        def on_error(e: Exception):
            print(e)

        def add_device_button(device: dict):
            button = QtWidgets.QPushButton("{volume}\n{make} - {model}".format(
                volume=device["volid"] or "No disc inserted...",
                make=device["make"],
                model=device["model"]
            ))
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            button.clicked.connect(lambda: self.load_device(device))
            if not device["volid"]:
                button.setEnabled(False)
            device_list = self.ui.deviceListDevices_2.layout()
            device_list.insertWidget(device_list.count() - 1 if not device["volid"] else 0, button)

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.scanned_devices.connect(add_device_button)

        self.thread.started.connect(self.worker.scan_devices)
        self.thread.start()

    def load_device(self, device: dict):
        """
        Load device, get disc object, get disc information.
        Currently only supports DVD discs.
        """
        self.thread = QtCore.QThread()
        self.worker = DeviceWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.ui.deviceListDevices_2.setEnabled(False)
            self.ui.refreshIcon.setEnabled(False)
            self.ui.progressBar.hide()
            self.ui.backupButton.hide()
            self.ui.discInfoFrame.hide()
            self.ui.discInfoList.clear()
            self.ui.statusbar.showMessage("Loading device %s - %s..." % (device["make"], device["model"]))

            if self.ui.backupButton.isEnabled():
                self.ui.backupButton.clicked.disconnect()

        def on_finish(_: int):
            self.ui.deviceListDevices_2.setEnabled(True)
            self.ui.refreshIcon.setEnabled(True)
            self.ui.backupButton.setEnabled(True)
            self.ui.backupButton.show()
            self.ui.discInfoFrame.show()
            self.ui.statusbar.showMessage("Loaded device %s - %s..." % (device["make"], device["model"]))

        def on_error(e: Exception):
            print(e)

        def get_dvd(dvd: Dvd):
            self.ui.discInfoList.clear()
            disc_id = dvd.compute_crc_id()
            disc_id_tree = QtWidgets.QTreeWidgetItem(["Disc ID", disc_id])
            self.ui.discInfoList.addTopLevelItem(disc_id_tree)

            pvd = dvd.get_primary_descriptor()
            pvd_tree = QtWidgets.QTreeWidgetItem(["Primary Volume Descriptor"])
            for k, v in pvd.items():
                pvd_tree.addChild(QtWidgets.QTreeWidgetItem([k, repr(v)]))
            self.ui.discInfoList.addTopLevelItem(pvd_tree)

            self.ui.discInfoList.expandToDepth(0)
            self.ui.discInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            self.ui.backupButton.clicked.connect(lambda: self.backup_disc(device, dvd))

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.dvd.connect(get_dvd)

        self.worker.device.connect(self.worker.load_device)
        self.thread.started.connect(lambda: self.worker.device.emit(device))
        self.thread.start()

    def backup_disc(self, device: dict, disc: Dvd):
        """Backup loaded disc to an ISO file."""
        out_dir = QtWidgets.QFileDialog.getExistingDirectory(None, "Backup Disc Image", "")
        if not out_dir:
            self.log.debug("Cancelled Backup as no file was provided.")
            return

        self.thread = QtCore.QThread()
        self.worker = DeviceWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.ui.progressBar.show()
            self.ui.backupButton.setEnabled(False)
            self.ui.statusbar.showMessage(
                "Backing up %s (%s - %s)..." % (device["volid"], device["make"], device["model"])
            )

        def on_progress(n: float):
            self.ui.progressBar.setValue(n)
            self.ui.backupButton.setText("Backing up... %d%%" % math.floor(n))

        def on_finish():
            self.ui.backupButton.setText("Backup")
            self.ui.statusbar.showMessage(
                "Backed up %s (%s - %s)..." % (device["volid"], device["make"], device["model"])
            )
            self.ui.backupButton.setEnabled(True)

        def on_error(e: Exception):
            print(e)

        self.thread.started.connect(manage_state)
        self.worker.progress.connect(on_progress)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)

        self.worker.disc.connect(self.worker.backup_disc)
        self.thread.started.connect(lambda: self.worker.disc.emit(disc, out_dir))
        self.thread.start()

    @staticmethod
    def open() -> QtWidgets.QMainWindow:
        loader = QUiLoader()
        loader.setWorkingDirectory(QtCore.QDir(str(cfg.root_dir)))
        ui_file = QtCore.QFile(str(cfg.root_dir / "ui" / "MainWindow.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)
        widget = loader.load(ui_file)
        widget.setWindowFlags(QtCore.Qt.Window)
        ui_file.close()
        return widget
