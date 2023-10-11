import math
import traceback
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Optional

from pycdlib.dates import VolumeDescriptorDate
from pycdlib.headervd import FileOrTextIdentifier
from PySide6 import QtCore
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (QFileDialog, QHeaderView, QMainWindow, QMessageBox, QPushButton, QTreeWidgetItem,
                               QVBoxLayout)

from pslipstream import __version__
from pslipstream.config import SYSTEM_INFO, config
from pslipstream.device import Device
from pslipstream.dvd import Dvd
from pslipstream.gui.main_window_ui import Ui_MainWindow  # type: ignore[attr-defined]
from pslipstream.gui.workers import DEVICE_LOADER, DEVICE_READER, DEVICE_SCANNER, WORKER_THREAD
from pslipstream.helpers import convert_iso_descriptor_date


class MainWindow(QMainWindow):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Slipstream v{__version__}")
        self.setMinimumSize(1000, 400)

        self.reset_ui()
        self.setup_logic()

    def reset_ui(self) -> None:
        """Reset the UI to initial startup state."""
        self.ui.backupButton.setEnabled(False)
        self.ui.backupButton.hide()
        self.ui.progressBar.hide()
        self.ui.discInfoFrame.hide()

        self.clear_device_list()

        for entry in config.recently_opened:
            self.add_recent_entry(entry)

    def setup_logic(self) -> None:
        """Link Signals/Slots, add startup calls."""
        # menu bar actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about)

        # device list
        DEVICE_SCANNER.started.connect(self.on_device_scan_start)
        DEVICE_SCANNER.finished.connect(self.on_device_scan_finish)
        DEVICE_SCANNER.error.connect(self.on_device_scan_error)
        DEVICE_SCANNER.scanned_device.connect(self.add_device_button)
        self.ui.refreshIcon.clicked.connect(DEVICE_SCANNER.scan)

        # disc info
        DEVICE_LOADER.started.connect(self.on_disc_load_start)
        DEVICE_LOADER.finished.connect(self.on_disc_load_finish)
        DEVICE_LOADER.error.connect(self.on_disc_load_error)
        DEVICE_LOADER.disc_loaded.connect(self.load_disc_info)

        # disc backup
        DEVICE_READER.started.connect(self.on_disc_read_start)
        DEVICE_READER.finished.connect(self.on_disc_read_finish)
        DEVICE_READER.error.connect(self.on_disc_read_error)
        DEVICE_READER.progress.connect(self.on_disc_read_progress)
        self.ui.backupButton.clicked.connect(lambda: (
            self.start_backup(DEVICE_LOADER.disc)
        ) if DEVICE_LOADER.disc else (
            QMessageBox.critical(self, "Error", "You somehow clicked Backup before a Disc was loaded.")
        ))

        # startup
        WORKER_THREAD.started.connect(DEVICE_SCANNER.scan)
        WORKER_THREAD.start()

    # Menu Bar #

    def open_file(self, device: Optional[Device] = None) -> None:
        """Open a Disc file and add a Pseudo-device Button to the Device list."""
        if not device:
            loc = QFileDialog.getOpenFileName(
                self,
                "Backup Disc Image",
                str(config.last_opened_directory or ""),
                "ISO files (*.iso);;DVD IFO files (*.ifo)"
            )
            if not loc[0]:
                return
            device = Device(
                target=loc[0],
                medium="DVD",  # TODO: Don't presume DVD
                volume_id=Path(loc[0]).name
            )

        self.add_device_button(device)
        DEVICE_LOADER.load_dvd(device)

        if not any(x.text() == device.target for x in self.ui.menuOpen_Recent.actions()):
            self.add_recent_entry(device)
            config.recently_opened.append(device)

        config.last_opened_directory = Path(device.target).parent

    def about(self) -> None:
        """Displays the Help->About Message Box."""
        QMessageBox.about(
            self,
            "About Slipstream",
            f"Slipstream v{__version__} [{SYSTEM_INFO}]" +
            f"<p>Copyright (C) 2020-{datetime.now().year} rlaphoenix</p>" +
            "<p>The most informative Home-media backup solution.<br/>"
            "<a href='https://github.com/rlaphoenix/Slipstream' style='color:white'>"
            "https://github.com/rlaphoenix/Slipstream"
            "</a></p>"
        )

    def add_recent_entry(self, device: Device) -> None:
        """Add an Entry to the File->Open Recent Menu bar list."""
        recent_entry = QAction(self)
        recent_entry.text()
        recent_entry.setText(device.target)
        recent_entry.triggered.connect(partial(self.open_file, device))
        self.ui.menuOpen_Recent.addAction(recent_entry)
        self.ui.menuOpen_Recent.setEnabled(True)

    # Device List #

    def clear_device_list(self) -> None:
        """Clear the List of Disc Reader Devices."""
        for device in self.ui.deviceListDevices_2.children():
            if isinstance(device, QPushButton):
                device.setParent(None)

    def add_device_button(self, device: Device) -> None:
        """Add a new Disc Reader Device Button to the List."""
        for d in self.ui.deviceListDevices_2.children():
            if isinstance(d, QPushButton) and d.objectName() == device.target:
                return

        no_disc = not bool(device.volume_id)

        button = QPushButton(
            f"{device.volume_id or 'No disc inserted...'}\n"
            f"{device.make} - {device.model}"
        )
        button.setObjectName(device.target)
        button.setCursor(QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button.clicked.connect(partial(DEVICE_LOADER.device.emit, device))

        if no_disc:
            button.setEnabled(False)

        device_list: QVBoxLayout = self.ui.deviceListDevices_2.layout()
        device_list.insertWidget(device_list.count() - 1 if no_disc else 0, button)

    def on_device_scan_start(self) -> None:
        self.ui.refreshIcon.setEnabled(False)
        self.ui.statusbar.showMessage("Scanning devices...")
        self.clear_device_list()

        self.ui.progressBar.hide()
        self.ui.backupButton.hide()
        self.ui.discInfoFrame.hide()
        self.ui.discInfoList.clear()

    def on_device_scan_finish(self, device_count: int) -> None:
        self.ui.refreshIcon.setEnabled(True)
        self.ui.statusbar.showMessage(f"Found {device_count} devices")

    def on_device_scan_error(self, error: Exception) -> None:
        traceback.print_exception(error)
        QMessageBox.critical(
            self,
            "Error",
            "An unexpected error occurred while scanning for Disc Reader Devices:\n\n" +
            "\n".join(traceback.format_exception(error))
        )

    # Disc Info #

    def load_disc_info(self, disc: Dvd) -> None:
        """Load Disc Information."""
        self.ui.discInfoList.clear()
        disc_id = disc.compute_crc_id()
        disc_id_tree = QTreeWidgetItem(["Disc ID", disc_id])
        self.ui.discInfoList.addTopLevelItem(disc_id_tree)

        pvd_tree = QTreeWidgetItem(["Primary Volume Descriptor"])
        for k, v in {k: disc.cdlib.pvd.__getattribute__(k) for k in disc.cdlib.pvd.__slots__}.items():
            if isinstance(v, FileOrTextIdentifier):
                v = v.text
            elif isinstance(v, VolumeDescriptorDate):
                v = convert_iso_descriptor_date(v)
            pvd_tree.addChild(QTreeWidgetItem([k, repr(v)]))
        self.ui.discInfoList.addTopLevelItem(pvd_tree)

        self.ui.discInfoList.expandToDepth(0)
        self.ui.discInfoList.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def on_disc_load_start(self, device: Device) -> None:
        self.ui.deviceListDevices_2.setEnabled(False)
        self.ui.refreshIcon.setEnabled(False)
        self.ui.progressBar.hide()
        self.ui.backupButton.hide()
        self.ui.discInfoFrame.hide()
        self.ui.discInfoList.clear()
        self.ui.statusbar.showMessage(f"Loading device {device.make} - {device.model}...")

    def on_disc_load_finish(self, device: Device) -> None:
        self.ui.deviceListDevices_2.setEnabled(True)
        self.ui.refreshIcon.setEnabled(True)
        self.ui.backupButton.setEnabled(True)
        self.ui.backupButton.show()
        self.ui.discInfoFrame.show()
        self.ui.statusbar.showMessage(f"Loaded device {device.make} - {device.model}...")

    def on_disc_load_error(self, error: Exception) -> None:
        traceback.print_exception(error)
        QMessageBox.critical(
            self,
            "Error",
            "An unexpected error occurred while Loading a Disc Reader Device:\n\n" +
            "\n".join(traceback.format_exception(error))
        )

    # Disc Backup #

    def start_backup(self, disc: Dvd) -> None:
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Disc Image",
            str(Path(
                config.last_opened_directory or "",
                disc.cdlib.pvd.volume_identifier.replace(b"\x00", b"").strip().decode() + ".ISO"
            )),
            "Disc Images (*.ISO, *.BIN);;All Files (*)"
        )
        if not save_path:
            return
        DEVICE_READER.disc.emit(disc, Path(save_path))

    def on_disc_read_progress(self, n: float) -> None:
        self.ui.progressBar.setValue(math.floor(n))
        self.ui.backupButton.setText(f"Backing up... {math.floor(n)}%")

    def on_disc_read_start(self, disc: Dvd) -> None:
        self.ui.progressBar.show()
        self.ui.progressBar.setValue(0)
        self.ui.backupButton.setEnabled(False)
        self.ui.statusbar.showMessage(
            f"Backing up {disc.device} ({disc.cdlib.pvd.volume_identifier.decode('utf8').strip()})..."
        )

    def on_disc_read_finish(self, disc: Dvd) -> None:
        self.ui.backupButton.setText("Backup")
        self.ui.statusbar.showMessage(
            f"Backed up {disc.device} ({disc.cdlib.pvd.volume_identifier.decode('utf8').strip()})..."
        )
        self.ui.backupButton.setEnabled(True)

    def on_disc_read_error(self, error: Exception) -> None:
        traceback.print_exception(error)
        QMessageBox.critical(
            self,
            "Error",
            "An unexpected error occurred while Backing up a Disc:\n\n" +
            "\n".join(traceback.format_exception(error))
        )
