from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

from pycdlib import PyCdlib
from pycdlib.pycdlibexception import PyCdlibInvalidInput
from pydvdcss.dvdcss import DvdCss
from pydvdid_m import DvdId
from PySide6.QtCore import SignalInstance
from tqdm import tqdm

from pslipstream.exceptions import SlipstreamNoKeysObtained, SlipstreamReadError, SlipstreamSeekError


class Dvd:
    def __init__(self) -> None:
        self.log = logging.getLogger("Dvd")
        self.cdlib: PyCdlib = PyCdlib()
        self.dvdcss: DvdCss = DvdCss()
        self.device: Optional[str] = None
        self.reader_position: int = 0
        self.vob_lba_offsets: List[Tuple[int, int]] = []

    def __enter__(self) -> Dvd:
        return self

    def __exit__(self, *_: Any, **__: Any) -> None:
        self.dispose()

    def dispose(self) -> None:
        self.log.info("Disposing Dvd object...")
        if self.cdlib:
            try:
                self.cdlib.close()
            except PyCdlibInvalidInput:
                pass
        if self.dvdcss:
            self.dvdcss.dispose()
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
        self.device = dev
        self.log.info("Opening '%s'...", dev)
        self.cdlib.open(rf"\\.\{dev}" if dev.endswith(":") else dev)
        self.log.info("Loaded Device in PyCdlib...")
        self.dvdcss.open(dev)
        self.log.info("Loaded Device in PyDvdCss...")
        self.log.info("DVD opened and ready...")

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
        t = tqdm(total=last_lba + 1, unit="sectors")

        while current_lba <= last_lba:
            data = self.read(current_lba, min(self.dvdcss.BLOCK_BUFFER, last_lba - current_lba + 1))
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

        ret = self.dvdcss.read(sectors, [self.dvdcss.NO_FLAGS, self.dvdcss.READ_DECRYPT][in_title])
        read_sectors = len(ret) // self.cdlib.pvd.log_block_size
        if read_sectors < 0:
            raise SlipstreamReadError(f"An unexpected read error occurred reading {first_lba}->{first_lba + sectors}")
        if read_sectors != sectors:
            # we do not want to just reduce the requested sector count as there's
            # a chance that the pvd space size is just wrong/badly mastered
            request_too_large = first_lba + sectors > self.cdlib.pvd.space_size
            if not request_too_large or (first_lba + sectors) - self.cdlib.pvd.space_size != read_sectors:
                raise SlipstreamReadError(
                    f"Read {read_sectors} bytes, expected {sectors}, while reading {first_lba}->{first_lba + sectors}"
                )
        self.reader_position += read_sectors

        return ret
