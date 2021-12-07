import logging
import math
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMessageBox

from pslipstream.config import config, Directories, System, Project
from pslipstream.device import Device
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

        for entry in config.recently_opened:
            self.add_recent_entry(entry)

        self.ui.backupButton.setEnabled(False)
        self.ui.backupButton.hide()
        self.ui.discInfoFrame.hide()
        self.ui.progressBar.hide()

    def connect_io(self):
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionExit.triggered.connect(self.ui.close)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.refreshIcon.clicked.connect(self.scan_devices)

    def about(self):
        QMessageBox.about(
            self.ui,
            "About %s" % Project.name,
            ("%s v%s [%s]" % (Project.name, Project.version, System.Info)) +
            ("<p>%s</p>" % Project.copyright) +
            ("<p>{0}<br/><a href='{1}' style='color:white'>{1}</a></p>".format(Project.description, Project.url))
        )

    def clear_device_list(self):
        for device in self.ui.deviceListDevices_2.children():
            if isinstance(device, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                device.setParent(None)

    def add_device_button(self, device: Device):
        for d in self.ui.deviceListDevices_2.children():
            if isinstance(d, QtWidgets.QPushButton):
                if d.objectName() == device.target:
                    return

        no_disc = not bool(device.volume_id)
        button = QtWidgets.QPushButton("{volume}\n{make} - {model}".format(
            volume=device.volume_id or "No disc inserted...",
            make=device.make,
            model=device.model
        ))
        button.setObjectName(device.target)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.clicked.connect(lambda: self.load_device(device))
        if no_disc:
            button.setEnabled(False)

        device_list = self.ui.deviceListDevices_2.layout()
        device_list.insertWidget(device_list.count() - 1 if no_disc else 0, button)

    def add_recent_entry(self, device: Device):
        recent_entry = QtWidgets.QAction(self.ui)
        recent_entry.text()
        recent_entry.setText(device.target)
        recent_entry.triggered.connect(lambda: self.open_file(device))
        self.ui.menuOpen_Recent.addAction(recent_entry)
        self.ui.menuOpen_Recent.setEnabled(True)

    def open_file(self, device: Device = None):
        if not device:
            loc = QtWidgets.QFileDialog.getOpenFileName(
                self.ui,
                "Backup Disc Image",
                str(config.last_opened_directory or ""),
                "ISO files (*.iso);;DVD IFO files (*.ifo)"
            )
            if not loc[0]:
                self.log.debug("Cancelled Open File as no save path was provided.")
                return
            device = Device(
                target=loc[0],
                medium="DVD",  # TODO: Don't presume DVD
                volume_id=Path(loc[0]).name
            )

        self.add_device_button(device)
        self.load_device(device)

        if not any(x.text() == device.target for x in self.ui.menuOpen_Recent.actions()):
            self.add_recent_entry(device)
            config.recently_opened.append(device)

        config.last_opened_directory = Path(device.target).parent

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

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.scanned_devices.connect(self.add_device_button)

        self.thread.started.connect(self.worker.scan_devices)
        self.thread.start()

    def load_device(self, device: Device):
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
            self.ui.statusbar.showMessage("Loading device %s - %s..." % (device.make, device.model))

            if self.ui.backupButton.isEnabled():
                self.ui.backupButton.clicked.disconnect()

        def on_finish(_: int):
            self.ui.deviceListDevices_2.setEnabled(True)
            self.ui.refreshIcon.setEnabled(True)
            self.ui.backupButton.setEnabled(True)
            self.ui.backupButton.show()
            self.ui.discInfoFrame.show()
            self.ui.statusbar.showMessage("Loaded device %s - %s..." % (device.make, device.model))

        def on_error(e: Exception):
            print(e)

        def get_dvd(dvd: Dvd):
            self.ui.discInfoList.clear()
            disc_id = dvd.compute_crc_id()
            disc_id_tree = QtWidgets.QTreeWidgetItem(["Disc ID", disc_id])
            self.ui.discInfoList.addTopLevelItem(disc_id_tree)

            pvd_tree = QtWidgets.QTreeWidgetItem(["Primary Volume Descriptor"])
            for k, v in {k: dvd.cdlib.pvd.__getattribute__(k) for k in dvd.cdlib.pvd.__slots__}.items():
                pvd_tree.addChild(QtWidgets.QTreeWidgetItem([k, repr(v)]))
            self.ui.discInfoList.addTopLevelItem(pvd_tree)

            self.ui.discInfoList.expandToDepth(0)
            self.ui.discInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            if not device.volume_id:
                device.volume_id = dvd.cdlib.pvd.volume_identifier

            self.ui.backupButton.clicked.connect(lambda: self.backup_disc(device, dvd))

        self.thread.started.connect(manage_state)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        self.worker.dvd.connect(get_dvd)

        self.worker.device.connect(self.worker.load_device)
        self.thread.started.connect(lambda: self.worker.device.emit(device))
        self.thread.start()

    def backup_disc(self, device: Device, disc: Dvd):
        """Backup loaded disc to an ISO file."""
        save_path = QtWidgets.QFileDialog.getSaveFileName(
            self.ui,
            "Backup Disc Image",
            str(Path(
                config.last_opened_directory or "",
                disc.cdlib.pvd.volume_identifier.replace(b"\x00", b"").strip().decode() + ".ISO"
            )),
            "Disc Images (*.ISO, *.BIN);;All Files (*)"
        )[0]
        if not save_path:
            self.log.debug("Cancelled Backup as no file was provided.")
            return
        save_path = Path(save_path)

        self.thread = QtCore.QThread()
        self.worker = DeviceWorker()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        def manage_state():
            self.ui.progressBar.show()
            self.ui.progressBar.setValue(0)
            self.ui.backupButton.setEnabled(False)
            self.ui.statusbar.showMessage(
                "Backing up %s (%s - %s)..." % (device.volume_id, device.make, device.model)
            )

        def on_progress(n: float):
            self.ui.progressBar.setValue(n)
            self.ui.backupButton.setText("Backing up... %d%%" % math.floor(n))

        def on_finish():
            self.ui.backupButton.setText("Backup")
            self.ui.statusbar.showMessage(
                "Backed up %s (%s - %s)..." % (device.volume_id, device.make, device.model)
            )
            self.ui.backupButton.setEnabled(True)

        def on_error(e: Exception):
            print(e)

        self.thread.started.connect(manage_state)
        self.worker.progress.connect(on_progress)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)

        self.worker.disc.connect(self.worker.backup_disc)
        self.thread.started.connect(lambda: self.worker.disc.emit(disc, save_path))
        self.thread.start()

    @staticmethod
    def open() -> QtWidgets.QMainWindow:
        loader = QUiLoader()
        loader.setWorkingDirectory(QtCore.QDir(str(Directories.root)))
        ui_file = QtCore.QFile(str(Directories.root / "ui" / "MainWindow.ui"))
        ui_file.open(QtCore.QFile.ReadOnly)
        widget = loader.load(ui_file)
        widget.setWindowFlags(QtCore.Qt.Window)
        ui_file.close()
        return widget
