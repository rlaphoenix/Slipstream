import logging
import subprocess
import sys

import pythoncom
import wmi
from PySide2 import QtCore
from pycdlib import PyCdlib

from pslipstream import cfg
from pslipstream.device import Device
from pslipstream.dvd import Dvd


class DeviceWorker(QtCore.QObject):
    # input signals
    device = QtCore.Signal(dict)
    disc = QtCore.Signal(Dvd, str)
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
                self.scanned_devices.emit(Device(
                    target=drive.drive,  # e.g. "D:"
                    make=drive.name.split(" ")[0],
                    model=drive.name.split(" ")[1],
                    revision=drive.mfrAssignedRevisionLevel,
                    volume_id=drive.volumeName
                ))
            self.finished.emit(len(drives))
            return
        if cfg.linux:
            lsscsi = subprocess.check_output(["lsscsi"]).decode().splitlines()
            lsscsi = [x[9:].strip() for x in lsscsi]
            lsscsi = [[x for x in scsi.split(" ") if x] for scsi in lsscsi]
            lsscsi = [x for x in lsscsi if x[0] not in ["disk"]]
            for scsi in lsscsi:
                self.scanned_devices.emit(Device(
                    target=scsi[-1],
                    medium=scsi[0],
                    make=scsi[1],
                    model=" ".join([scsi[2]] if len(scsi) == 5 else scsi[2:(len(scsi) - 2)]),
                    revision=scsi[-2],
                    volume_id=self.get_volume_id(scsi[-1])
                ))
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

    def load_device(self, device: Device):
        try:
            pythoncom.CoInitialize()
            dvd = Dvd()  # TODO: assumes disc is a DVD
            dvd.open(device.target)
            self.dvd.emit(dvd)
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)

    def backup_disc(self, disc: Dvd, out_dir: str):
        try:
            disc.create_backup(out_dir, self.progress)
            self.finished.emit(0)
        except Exception as e:
            self.error.emit(e)
