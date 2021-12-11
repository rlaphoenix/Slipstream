import math
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QMessageBox

from pslipstream.config import config, Project, System
from pslipstream.device import Device
from pslipstream.dvd import Dvd
from pslipstream.ui import BaseWindow
from pslipstream.ui.DeviceWorker import DeviceWorker


class Main(BaseWindow):
    def __init__(self):
        super().__init__(name="main")

        self.window.setMinimumSize(1000, 400)
        self.window.backupButton.setEnabled(False)
        self.window.backupButton.hide()
        self.window.progressBar.hide()
        self.window.discInfoFrame.hide()
        # self.window.discInfoFrame.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.window.actionExit.triggered.connect(self.window.close)
        self.window.actionAbout.triggered.connect(self.about)
        self.window.actionOpen.triggered.connect(self.open_file)
        self.window.refreshIcon.clicked.connect(self.scan_devices)  # rename get_device_list

        self.clear_device_list()  # TODO: Remove example buttons from ui file instead?
        for entry in config.recently_opened:
            self.add_recent_entry(entry)

        self.scan_devices()

    def about(self) -> None:
        QMessageBox.about(
            self.window,
            f"About {Project.name}",
            f"{Project.name} v{Project.version} [{System.Info}]" +
            f"<p>{Project.copyright}</p>" +
            f"<p>{Project.description}<br/><a href='{Project.url}' style='color:white'>{Project.url}</a></p>"
        )

    def clear_device_list(self):
        for device in self.window.deviceListDevices_2.children():
            if isinstance(device, QtWidgets.QPushButton):
                # noinspection PyTypeChecker
                device.setParent(None)

    def add_device_button(self, device: Device):
        for d in self.window.deviceListDevices_2.children():
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

        device_list = self.window.deviceListDevices_2.layout()
        device_list.insertWidget(device_list.count() - 1 if no_disc else 0, button)

    def add_recent_entry(self, device: Device):
        recent_entry = QtWidgets.QAction(self.window)
        recent_entry.text()
        recent_entry.setText(device.target)
        recent_entry.triggered.connect(lambda: self.open_file(device))
        self.window.menuOpen_Recent.addAction(recent_entry)
        self.window.menuOpen_Recent.setEnabled(True)

    def open_file(self, device: Device = None):
        if not device:
            loc = QtWidgets.QFileDialog.getOpenFileName(
                self.window,
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

        if not any(x.text() == device.target for x in self.window.menuOpen_Recent.actions()):
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
            self.window.refreshIcon.setEnabled(False)
            self.window.progressBar.hide()
            self.window.backupButton.hide()
            self.window.discInfoFrame.hide()
            self.window.discInfoList.clear()
            self.window.statusbar.showMessage("Scanning devices...")

        def on_finish(n: int):
            self.window.refreshIcon.setEnabled(True)
            self.window.statusbar.showMessage("Found %d devices" % n)

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
            self.window.deviceListDevices_2.setEnabled(False)
            self.window.refreshIcon.setEnabled(False)
            self.window.progressBar.hide()
            self.window.backupButton.hide()
            self.window.discInfoFrame.hide()
            self.window.discInfoList.clear()
            self.window.statusbar.showMessage("Loading device %s - %s..." % (device.make, device.model))

            if self.window.backupButton.isEnabled():
                self.window.backupButton.clicked.disconnect()

        def on_finish(_: int):
            self.window.deviceListDevices_2.setEnabled(True)
            self.window.refreshIcon.setEnabled(True)
            self.window.backupButton.setEnabled(True)
            self.window.backupButton.show()
            self.window.discInfoFrame.show()
            self.window.statusbar.showMessage("Loaded device %s - %s..." % (device.make, device.model))

        def on_error(e: Exception):
            print(e)

        def get_dvd(dvd: Dvd):
            self.window.discInfoList.clear()
            disc_id = dvd.compute_crc_id()
            disc_id_tree = QtWidgets.QTreeWidgetItem(["Disc ID", disc_id])
            self.window.discInfoList.addTopLevelItem(disc_id_tree)

            pvd_tree = QtWidgets.QTreeWidgetItem(["Primary Volume Descriptor"])
            for k, v in {k: dvd.cdlib.pvd.__getattribute__(k) for k in dvd.cdlib.pvd.__slots__}.items():
                pvd_tree.addChild(QtWidgets.QTreeWidgetItem([k, repr(v)]))
            self.window.discInfoList.addTopLevelItem(pvd_tree)

            self.window.discInfoList.expandToDepth(0)
            self.window.discInfoList.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            if not device.volume_id:
                device.volume_id = dvd.cdlib.pvd.volume_identifier

            self.window.backupButton.clicked.connect(lambda: self.backup_disc(device, dvd))

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
            self.window,
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
            self.window.progressBar.show()
            self.window.progressBar.setValue(0)
            self.window.backupButton.setEnabled(False)
            self.window.statusbar.showMessage(
                "Backing up %s (%s - %s)..." % (device.volume_id, device.make, device.model)
            )

        def on_progress(n: float):
            self.window.progressBar.setValue(n)
            self.window.backupButton.setText("Backing up... %d%%" % math.floor(n))

        def on_finish():
            self.window.backupButton.setText("Backup")
            self.window.statusbar.showMessage(
                "Backed up %s (%s - %s)..." % (device.volume_id, device.make, device.model)
            )
            self.window.backupButton.setEnabled(True)

        def on_error(e: Exception):
            print(e)

        self.thread.started.connect(manage_state)
        self.worker.progress.connect(on_progress)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)

        self.worker.disc.connect(self.worker.backup_disc)
        self.thread.started.connect(lambda: self.worker.disc.emit(disc, save_path))
        self.thread.start()
