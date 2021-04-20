#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slipstream - The most informative Home-media backup solution.
Copyright (C) 2020 PHOENiX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

~~~

Class file that handles all DVD operations including loading,
reading, seeking, backing up, and more.
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Union

import pycdlib
import rlapydvdid
from PySide2.QtCore import Signal
from dateutil.tz import tzoffset
from pycdlib.headervd import PrimaryOrSupplementaryVD
from pydvdcss.dvdcss import DvdCss
from tqdm import tqdm

import pslipstream.cfg as cfg
from pslipstream.exceptions import SlipstreamSeekError, SlipstreamDiscInUse, SlipstreamNoKeysObtained, \
    SlipstreamReadError


class Dvd:
    def __init__(self):
        self.log = logging.getLogger("Dvd")
        self.device = None
        self.ready = False
        self.cdlib = None
        self.dvdcss = None
        self.reader_position = 0
        self.vob_lba_offsets = []

    def __enter__(self):
        return self

    def __exit__(self, *_, **kwargs):
        self.dispose()

    def dispose(self):
        self.log.info("Disposing Dvd object...")
        if self.cdlib:
            self.cdlib.close()
        if self.dvdcss:
            self.dvdcss.dispose()
        self.__init__()  # reset everything

    def open(self, dev):
        """
        Open the device as a DVD with pycdlib and libdvdcss.

        pycdlib will be used to identify and extract information.
        libdvdcss will be used for reading, writing, and decrypting.

        Raises SlipstreamDiscInUse if you try to load the same disc that's
        already opened. You can open a different disc without an exception as
        it will automatically dispose the current disc before opening.
        """
        if self.dvdcss or self.cdlib:
            if dev != self.device:
                # dispose, and continue loading the new disc
                self.dispose()
            else:
                raise SlipstreamDiscInUse("The specified DVD device is already open in this instance.")
        self.device = dev
        self.log.info(f"Opening '{dev}'...")
        self.cdlib = pycdlib.PyCdlib()
        self.cdlib.open(rf"\\.\{dev}" if cfg.windows else dev)
        self.log.info("Initialised pycdlib instance successfully...")
        self.dvdcss = DvdCss()
        self.dvdcss.open(dev)
        self.log.info("Initialised pydvdcss instance successfully...")
        self.ready = True
        self.log.info("DVD opened and ready...")

    def compute_crc_id(self):
        """
        Get the CRC64 checksum known as the Media Player DVD ID.
        The algorithm used is the exact same one used by Microsoft's old Windows Media Center.
        """
        crc = str(rlapydvdid.compute(self.cdlib))
        self.log.info(f"Got CRC64 DVD ID: {crc}\n")
        return crc

    def get_pvd(self) -> PrimaryOrSupplementaryVD:
        """
        Get's and returns the Primary Volume Descriptor of the
        disc in a more accessible and parsed format.
        """

        def date_convert(d):
            if not d.year:
                return None
            return datetime(
                year=d.year, month=d.month, day=d.dayofmonth,
                hour=d.hour, minute=d.minute, second=d.second, microsecond=d.hundredthsofsecond,
                # offset the timezone, since ISO's dates are offsets of GMT in 15 minute intervals, we
                # need to calculate that but in seconds to pass to `tzoffset`.
                tzinfo=tzoffset("GMT", (15 * d.gmtoffset) * 60)
            )

        pvd = self.cdlib.pvd
        pvd.system_identifier = pvd.system_identifier.replace(b"\x00", b"").strip().decode() or None
        pvd.volume_identifier = pvd.volume_identifier.replace(b"\x00", b"").strip().decode() or None
        pvd.volume_creation_date = date_convert(pvd.volume_creation_date)
        pvd.volume_expiration_date = date_convert(pvd.volume_expiration_date)
        pvd.volume_effective_date = date_convert(pvd.volume_effective_date)
        self.log.info(f"Got Primary Volume Descriptor: {pvd}\n")
        return pvd

    def get_files(self, path="/", no_versions=True):
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
            size = int(child.get_data_length() / self.dvdcss.SECTOR_SIZE)
            self.log.debug(f"Found title file: {file_path}, lba: {lba}, size: {size}")
            yield file_path, lba, size

    def get_vob_lbas(self, crack_keys=False):
        """
        Get the LBA data for all VOB files in disc.
        Optionally seek with SEEK_KEY flag to obtain keys.

        Raises SlipstreamSeekError on seek failures.
        """
        # Create an array for holding the title data
        lba_data = []
        # Loop all files in disc:/VIDEO_TS
        for vob, lba, size in self.get_files("/VIDEO_TS"):
            # we only want vob files
            if os.path.splitext(vob)[-1] != ".VOB":
                continue
            # get title key
            if crack_keys:
                if lba == self.dvdcss.seek(lba, self.dvdcss.SEEK_KEY):
                    self.log.info(f"Got title key for {vob}")
                else:
                    raise SlipstreamSeekError(
                        f"Failed to seek the disc to {lba} while attempting to "
                        f"crack the title key for {os.path.basename(vob)}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Return lba data
        return lba_data

    def backup(self, out_dir: Union[Path, str], progress: Signal = None):
        """
        Create a full untouched (but decrypted) ISO backup of a DVD with all
        metadata intact.

        Parameters:
            out_dir: Directory to store the backup.
            progress: Signal to emit progress updates to.

        Raises:
            SlipstreamNoKeysObtained if no CSS keys were obtained when needed.
            SlipstreamReadError on unexpected read errors.
        """
        self.log.info("Starting DVD backup for %s" % self.device)

        pvd = self.get_pvd()
        fn = Path(out_dir) / ("%s.ISO.!ss" % pvd.volume_identifier)
        first_lba = 0  # lba values are 0-indexed
        current_lba = first_lba
        last_lba = pvd.space_size - 1
        disc_size = pvd.log_block_size * pvd.space_size

        self.log.debug(
            f"Reading sectors {first_lba:,} to {last_lba:,} with sector size {pvd.log_block_size:,} B.\n"
            f"Length: {last_lba + 1:,} sectors, {disc_size:,} bytes.\n"
            f'Saving to "{fn.with_suffix("")}"...'
        )

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
            sectors = min(self.dvdcss.BLOCK_BUFFER, last_lba - current_lba + 1)
            data = self.read(current_lba, sectors)
            read_sectors = len(data) // pvd.log_block_size
            # write the buffer to output file
            f.write(data)
            # increment the current sector and update the tqdm progress bar
            current_lba += read_sectors
            # write progress to GUI
            if progress:
                progress.emit((current_lba / last_lba) * 100)
            # write progress to CLI
            t.update(read_sectors)
        # Close file and tqdm progress bar
        f.close()
        t.close()

        fn.replace(fn.with_suffix(""))
        # Tell the user some output information
        self.log.info(
            "Finished DVD Backup!\n"
            f"Read a total of {current_lba:,} sectors ({os.path.getsize(fn):,}) bytes.\n"
        )

    def read(self, first_lba, sectors) -> bytes:
        """
        Efficiently read an amount of sectors from the disc while supporting decryption
        with libdvdcss (pydvdcss).

        Returns the amount of sectors read.
        Raises a SlipstreamSeekError on Seek Failures and SlipstreamReadError on Read Failures.
        """

        # we need to seek to the first sector. Otherwise we get faulty data.
        need_to_seek = first_lba != self.reader_position or first_lba == 0
        in_title = False
        entered_title = False

        # Make sure we never read encrypted and unencrypted data at once since libdvdcss
        # only decrypts the whole area of read sectors or nothing at all.
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
        read_sectors = len(ret) // self.dvdcss.SECTOR_SIZE
        if read_sectors != sectors:
            raise SlipstreamReadError(
                "Read %d bytes, expected %d, while reading %d->%d" % (
                    read_sectors, sectors, first_lba, first_lba + sectors
                )
            )
        if read_sectors < 0:
            raise SlipstreamReadError(f"An unexpected read error occurred reading {first_lba}->{first_lba + sectors}")
        self.reader_position += read_sectors

        return ret
