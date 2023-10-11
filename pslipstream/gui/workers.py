from pathlib import Path
from typing import Any, Optional

import pythoncom
from PySide6.QtCore import QObject, QThread, Signal
from wmi import WMI

from pslipstream.device import Device
from pslipstream.dvd import Dvd


class DeviceScanner(QObject):
    """QObject to Scan for Disc Reader Devices."""
    started = Signal()
    finished = Signal(int)
    error = Signal(Exception)
    scanned_device = Signal(Device)

    def scan(self) -> None:
        try:
            self.started.emit()
            # noinspection PyUnresolvedReferences
            pythoncom.CoInitialize()  # important!
            c = WMI()
            drives = c.Win32_CDROMDrive()
            for drive in drives:
                self.scanned_device.emit(Device(
                    target=drive.drive,
                    make=drive.name.split(" ")[0],
                    model=drive.name.split(" ")[1],
                    revision=drive.mfrAssignedRevisionLevel,
                    volume_id=drive.volumeName
                ))
            self.finished.emit(len(drives))
        except Exception as e:  # skipcq: PYL-W0703
            self.error.emit(e)


class DeviceLoader(QObject):
    """
    QObject to Load Disc Information from a Disc Reader Device.

    Note:
    - Currently only DVD Discs are supported.
    """
    started = Signal(Device)
    finished = Signal(Device)
    error = Signal(Exception)
    disc_loaded = Signal(Dvd)

    device = Signal(Device)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.device.connect(self.load_dvd)

        self.disc: Optional[Dvd] = None

    def load_dvd(self, device: Device) -> None:
        try:
            self.started.emit(device)
            # noinspection PyUnresolvedReferences
            pythoncom.CoInitialize()
            # TODO: assumes disc is a DVD
            disc = Dvd()
            disc.open(device.target)
            self.disc = disc
            self.disc_loaded.emit(disc)
            self.finished.emit(device)
        except Exception as e:  # skipcq: PYL-W0703
            self.error.emit(e)


class DeviceReader(QObject):
    """
    QObject to Read Data from a Disc Reader Device.

    Note:
    - Currently only DVD Discs are supported.
    - CSS (Content Scramble System) is automatically bypassed with libdvdcss.
    """
    started = Signal(Dvd)
    finished = Signal(Dvd)
    error = Signal(Exception)
    progress = Signal(float)

    disc = Signal(Dvd, Path)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.disc.connect(self.backup_dvd)

    def backup_dvd(self, disc: Dvd, save_path: Path) -> None:
        try:
            self.started.emit(disc)
            disc.backup(save_path, self.progress)
            self.finished.emit(disc)
        except Exception as e:  # skipcq: PYL-W0703
            self.error.emit(e)


WORKER_THREAD = QThread()

DEVICE_SCANNER = DeviceScanner()
DEVICE_SCANNER.moveToThread(WORKER_THREAD)

DEVICE_LOADER = DeviceLoader()
DEVICE_LOADER.moveToThread(WORKER_THREAD)

DEVICE_READER = DeviceReader()
DEVICE_READER.moveToThread(WORKER_THREAD)
