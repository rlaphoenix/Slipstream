from __future__ import annotations

import ctypes
import logging
import os
import struct
import sys
import time
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

from pycdlib import PyCdlib
from pycdlib.pycdlibexception import PyCdlibInvalidInput, PyCdlibInvalidISO
from pydvdcss.dvdcss import DvdCss
from pydvdid_m import DvdId
from PySide6.QtCore import SignalInstance
from tqdm import tqdm

from pslipstream import scsi
from pslipstream.config import config
from pslipstream.exceptions import SlipstreamNoKeysObtained, SlipstreamReadError, SlipstreamSeekError


def _register_libdvdcss() -> None:
    """
    Make the bundled libdvdcss DLL discoverable when running from source on Windows.

    The frozen build ships the DLL next to the executable, but a source checkout keeps it in the
    `submodules/libdvdcss` submodule. pydvdcss locates the library via ctypes' find_library, which
    on Windows searches PATH, so we prepend the architecture-specific submodule directory to it.
    On Linux/macOS, libdvdcss is provided by the system package manager instead.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return  # frozen build bundles the DLL itself
    if sys.platform != "win32":
        return  # the submodule holds Windows DLLs; other platforms use the system libdvdcss
    bits = 8 * struct.calcsize("P")
    dll_dir = Path(__file__).resolve().parents[1] / "submodules" / "libdvdcss" / "1.5.0" / f"{bits}-bit"
    if (dll_dir / "libdvdcss-2.dll").is_file():
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")
        os.add_dll_directory(str(dll_dir))


_register_libdvdcss()


class Dvd:
    def __init__(self) -> None:
        self.log = logging.getLogger("Dvd")
        self.cdlib: PyCdlib = PyCdlib()
        self.dvdcss: DvdCss = DvdCss()
        self.device: Optional[str] = None
        self.reader_position: int = 0
        self.vob_lba_offsets: List[Tuple[int, int]] = []
        self._scsi: Optional[scsi.ScsiReader] = None  # raw SCSI fallback reader for sectors libdvdcss can't read
        # pydvdcss declares dvdcss_error() as returning an int, so its DvdCss.error() crashes when building
        # a read-error message; correct the return type so libdvdcss read errors surface legibly.
        self.dvdcss._library.dvdcss_error.restype = ctypes.c_char_p

    def __enter__(self) -> Dvd:
        return self

    def __exit__(self, *_: Any, **__: Any) -> None:
        self.dispose()

    def dispose(self) -> None:
        self.log.info("Disposing Dvd object...")
        if self.cdlib:
            try:
                self.cdlib.close()
            except (PyCdlibInvalidInput, AttributeError):
                # AttributeError: pycdlib's raw-device wrapper has no close() to call
                pass
        if self.dvdcss:
            self.dvdcss.dispose()
        if self._scsi is not None:
            self._scsi.close()
            self._scsi = None
        self.device = None
        self.reader_position = 0
        self.vob_lba_offsets = []

    def open(self, dev: str) -> None:
        """
        Open the device as a DVD with pycdlib and libdvdcss.

        pycdlib will be used to identify and extract information.
        libdvdcss will be used for reading, writing, and decrypting.

        Raises SlipstreamDiscInUse if you try to load the same disc that's
        already opened. You can open a different disc without an exception as
        it will automatically dispose the current disc before opening.
        """
        if self.cdlib:
            try:
                self.cdlib.close()
            except PyCdlibInvalidInput:
                pass
        if self.dvdcss:
            self.dvdcss.close()
        if self._scsi is not None:
            self._scsi.close()
            self._scsi = None
        self.device = dev
        self.log.info("Opening '%s'...", dev)
        self._open_cdlib(rf"\\.\{dev}" if dev.endswith(":") else dev)
        self.log.info("Loaded Device in PyCdlib...")
        # libdvdcss reads these from the environment at open time. pydvdcss's set_cracking_mode("unset")
        # wrongly writes the literal string "unset" instead of removing the variable, so handle it here.
        if config.css_crack_mode == "unset":
            os.environ.pop("DVDCSS_METHOD", None)
        else:
            self.dvdcss.set_cracking_mode(config.css_crack_mode)
        self.dvdcss.set_verbosity(config.css_verbosity)
        self.dvdcss.open(dev)
        self.log.info("Loaded Device in PyDvdCss...")
        self._open_scsi(dev)
        self.log.info("DVD opened and ready...")

    def _open_scsi(self, dev: str) -> None:
        """Open a raw SCSI reader used to recover sectors libdvdcss cannot read (Windows only)."""
        if sys.platform != "win32":
            return
        device_path = rf"\\.\{dev}" if dev.endswith(":") else dev
        try:
            self._scsi = scsi.ScsiReader(device_path, config.scsi_max_transfer_sectors)
        except OSError as e:
            self.log.warning("Raw SCSI fallback unavailable for '%s': %s", dev, e)
            self._scsi = None

    def _open_cdlib(self, device_path: str) -> None:
        """
        Open the device in pycdlib, retrying on intermittent disc-parse failures.

        DVDs are UDF-bridge discs, so pycdlib always parses the UDF anchors. An optical drive can
        momentarily return incomplete data (e.g. while spinning up), making this fail with errors
        like "Expected at least 2 UDF Anchors" on one attempt yet succeed on the next. A failed
        open leaves the PyCdlib instance in a partial state, so each retry uses a fresh instance.

        Raises the last PyCdlibInvalidISO if every attempt fails.
        """
        attempts = max(1, config.pycdlib_open_attempts)
        last_error: Optional[PyCdlibInvalidISO] = None
        for attempt in range(1, attempts + 1):
            try:
                self.cdlib.open(device_path)
                if attempt > 1:
                    self.log.info("pycdlib opened on attempt %d/%d", attempt, attempts)
                return
            except PyCdlibInvalidISO as e:
                last_error = e
                self.log.warning("pycdlib open attempt %d/%d failed (%s)", attempt, attempts, e)
                try:
                    self.cdlib.close()
                except PyCdlibInvalidInput:
                    pass
                self.cdlib = PyCdlib()  # fresh instance for a clean retry
                if attempt < attempts:
                    time.sleep(config.pycdlib_open_retry_delay)
        assert last_error is not None  # loop always sets it before exhausting
        raise last_error

    def compute_crc_id(self) -> str:
        """
        Get the CRC64 checksum known as the Media Player DVD ID.
        The algorithm used is the exact same one used by Microsoft's old Windows Media Center.
        """
        crc = str(DvdId(self.cdlib).checksum)
        self.log.info("Got CRC64 DVD ID: %s", crc)
        return crc

    def get_files(self, path: str = "/", no_versions: bool = True) -> Generator[Tuple[str, int, int], None, None]:
        """
        Read and list file paths directly from the disc device file system
        which doesn't require the device to be mounted

        Returns a tuple generator of the file path which will be
        absolute-paths relative to the root of the device, the Logical
        Block Address (LBA), and the Size (in sectors).
        """
        for child in self.cdlib.list_children(iso_path=path):
            file_path = child.file_identifier().decode()
            # skip the `.` and `..` paths
            if file_path in [".", ".."]:
                continue
            # remove the semicolon and version number
            if no_versions and ";" in file_path:
                file_path = file_path.split(";")[0]
            # join it to root to be absolute
            file_path = os.path.join("/", path, file_path)
            # get lba
            lba = child.extent_location()
            # get size in sectors
            size = child.get_data_length() // self.cdlib.pvd.log_block_size
            self.log.debug("Found title file: %s, lba: %d, size: %d", file_path, lba, size)
            yield file_path, lba, size

    def get_vob_lbas(self, crack_keys: bool = False) -> List[Tuple[int, int]]:
        """
        Get the LBA data for all VOB files in disc.
        Optionally seek with SEEK_KEY flag to obtain keys.

        Raises SlipstreamSeekError on seek failures.
        """
        # Create an array for holding the title data
        lba_data: List[Tuple[int, int]] = []
        # Loop all files in disc:/VIDEO_TS
        for vob, lba, size in self.get_files("/VIDEO_TS"):
            # we only want vob files
            if os.path.splitext(vob)[-1] != ".VOB":
                continue
            # get title key
            if crack_keys:
                if lba == self.dvdcss.seek(lba, self.dvdcss.SEEK_KEY):
                    self.log.info("Got title key for %s", vob)
                else:
                    raise SlipstreamSeekError(
                        f"Failed to seek the disc to {lba} while attempting to "
                        f"crack the title key for {os.path.basename(vob)}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Return lba data
        return lba_data

    def backup(self, save_path: Path, progress: Optional[SignalInstance] = None) -> None:
        """
        Create a full untouched (but decrypted) ISO backup of a DVD with all
        metadata intact.

        Parameters:
            save_path: Path to store backup.
            progress: Signal to emit progress updates to.

        Raises:
            SlipstreamNoKeysObtained if no CSS keys were obtained when needed.
            SlipstreamReadError on unexpected read errors.
        """
        self.log.info("Starting DVD backup for %s", self.device)

        fn = save_path.with_suffix(".ISO.!ss")
        first_lba = 0  # lba values are 0-indexed
        current_lba = first_lba
        last_lba = self.cdlib.pvd.space_size - 1
        disc_size = self.cdlib.pvd.log_block_size * self.cdlib.pvd.space_size

        self.log.debug(  # skipcq: PYL-W1203
            f"Reading sectors {first_lba:,} to {last_lba:,} with sector size {self.cdlib.pvd.log_block_size:,} B."
        )
        self.log.debug(f"Length: {last_lba + 1:,} sectors, {disc_size:,} bytes")  # skipcq: PYL-W1203
        self.log.debug('Saving to "%s"...', fn.with_suffix(""))

        if self.dvdcss.is_scrambled():
            self.log.debug("DVD is scrambled. Checking if all CSS keys can be cracked. This might take a while.")
            self.vob_lba_offsets = self.get_vob_lbas(crack_keys=True)
            if not self.vob_lba_offsets:
                raise SlipstreamNoKeysObtained("No CSS title keys were returned, unable to decrypt.")
        else:
            self.log.debug("DVD isn't scrambled. CSS title key cracking skipped.")

        f = fn.open("wb")
        t = tqdm(total=last_lba + 1, unit="sectors", disable=sys.stderr is None)

        while current_lba <= last_lba:
            data = self.read(current_lba, min(max(1, config.read_buffer_sectors), last_lba - current_lba + 1))
            f.write(data)
            read_sectors = len(data) // self.cdlib.pvd.log_block_size
            current_lba += read_sectors
            if progress:
                progress.emit((current_lba / last_lba) * 100)
            t.update(read_sectors)

        f.close()
        t.close()

        fn = fn.replace(fn.with_suffix(""))
        self.log.info("Finished DVD Backup!")
        self.log.info(f"Read a total of {current_lba:,} sectors ({os.path.getsize(fn):,}) bytes)")  # skipcq: PYL-W1203

    def read(self, first_lba: int, sectors: int) -> bytes:
        """
        Efficiently read an amount of sectors from the disc while supporting decryption
        with libdvdcss (pydvdcss).

        Returns the amount of sectors read.
        Raises a SlipstreamSeekError on Seek Failures and SlipstreamReadError on Read Failures.
        """
        # must seek to the first sector, otherwise, we get faulty data
        need_to_seek = first_lba != self.reader_position or first_lba == 0
        in_title = False
        entered_title = False

        # Make sure we never read encrypted and unencrypted data at once since libdvdcss
        # only decrypts the whole area of read sectors or nothing at all
        for title_start, title_end in self.vob_lba_offsets:
            title_end += title_start - 1

            # update key when entering a new title
            # FIXME: we also need this if we seek into a new title (not only the start of the title)
            if title_start == first_lba:
                entered_title = need_to_seek = in_title = True

            # if first_lba < title_start and first_lba + sectors > title_start:
            if first_lba < title_start < first_lba + sectors:
                # read range will read beyond or on a title,
                # let's read up to right before the next title start
                sectors = title_start - first_lba

            # if first_lba < title_end and first_lba + sectors > title_end:
            if first_lba < title_end < first_lba + sectors:
                # read range will read beyond or on a title,
                # let's read up to right before the next title start
                sectors = title_end - first_lba + 1

            # is our read range part of one title
            if first_lba >= title_start and first_lba + (sectors - 1) <= title_end:
                in_title = True

        if need_to_seek:
            if entered_title:
                flags = self.dvdcss.SEEK_KEY
            elif in_title:
                flags = self.dvdcss.SEEK_MPEG
            else:
                flags = self.dvdcss.NO_FLAGS

            # refresh the key status for this sector's data
            self.reader_position = self.dvdcss.seek(first_lba, flags)
            if self.reader_position != first_lba:
                raise SlipstreamSeekError(f"Failed to seek the disc to {first_lba} while doing a device read.")

        block_size = self.cdlib.pvd.log_block_size
        try:
            ret = self.dvdcss.read(sectors, [self.dvdcss.NO_FLAGS, self.dvdcss.READ_DECRYPT][in_title])
        except OSError as e:
            # libdvdcss returned a read error (pydvdcss raises). Treat it as nothing read so the SCSI
            # fallback below can try, then fall through to a clear error if that cannot recover it either.
            self.log.warning("libdvdcss read error at %d->%d: %s", first_lba, first_lba + sectors, e)
            ret = b""
        read_sectors = len(ret) // block_size

        if read_sectors < sectors:
            # libdvdcss could not read part of this range - e.g. a sector outside the logical volume, or one
            # the volume path failed on. Recover the remainder with a raw SCSI read of the device, which
            # takes a different path and can reach it. SCSI returns raw (undecrypted) bytes, so this is only
            # valid outside a CSS title; an encrypted gap cannot be substituted and is a genuine read error.
            missing = sectors - read_sectors
            recover_from = first_lba + read_sectors
            recovered = self._recover_via_scsi(recover_from, missing) if not in_title else None
            if recovered is None:
                raise SlipstreamReadError(
                    f"Read {read_sectors} sectors, expected {sectors}, while reading {first_lba}->{first_lba + sectors}"
                )
            self.log.info("Recovered %d sector(s) at %d via a raw SCSI read of the device.", missing, recover_from)
            ret += recovered

        # Advance only by what libdvdcss itself read; any SCSI-recovered gap leaves libdvdcss positioned
        # behind, so the next read re-seeks to resync.
        self.reader_position += read_sectors

        return ret

    def _recover_via_scsi(self, lba: int, count: int) -> Optional[bytes]:
        """
        Read `count` unencrypted sectors libdvdcss could not, via a raw SCSI read (Windows SPTI). Retries
        a few times since a drive can transiently fail. Returns the bytes, or None if unavailable/unreadable.
        """
        if self._scsi is None:
            return None
        expected = count * self.cdlib.pvd.log_block_size
        for _ in range(max(1, config.scsi_read_attempts)):
            data = self._scsi.read(lba, count)
            if data is not None and len(data) == expected:
                return data
        return None
