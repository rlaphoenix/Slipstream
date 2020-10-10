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

import builtins as g
import os
import sys
from datetime import datetime

import pycdlib
import rlapydvdid
from dateutil.tz import tzoffset
from pydvdcss.dvdcss import DvdCss
from tqdm import tqdm

import pslipstream.cfg as cfg
from pslipstream.exceptions import SlipstreamSeekError, SlipstreamDiscInUse, SlipstreamNoKeysObtained, \
    SlipstreamReadError
from pslipstream.helpers import asynchronous_auto


class Dvd:
    def __init__(self):
        self.dev = None
        self.ready = False
        self.cdlib = None
        self.dvdcss = None
        self.reader_position = 0
        self.vob_lba_offsets = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.dispose()

    def dispose(self):
        g.LOG.write(f"Disposing Dvd object...")
        if self.cdlib:
            self.cdlib.close()
        if self.dvdcss:
            self.dvdcss.dispose()
        self.__init__()  # reset everything
        g.PROGRESS.c.Call(0)

    @asynchronous_auto
    def open(self, dev, js=None):
        """
        Open the device as a DVD with pycdlib and libdvdcss.

        pycdlib will be used to identify and extract information.
        libdvdcss will be used for reading, writing, and decrypting.

        Raises SlipstreamDiscInUse if you try to load the same disc that's
        already opened. You can open a different disc without an exception as
        it will automatically dispose the current disc before opening.
        """
        if self.dvdcss or self.cdlib:
            if dev != self.dev:
                # dispose, and continue loading the new disc
                self.dispose()
            else:
                raise SlipstreamDiscInUse("The specified DVD device is already open in this instance.")
        self.dev = dev
        g.LOG.write(f"Opening {dev} as a DVD...")
        self.cdlib = pycdlib.PyCdlib()
        self.cdlib.open("\\\\.\\" + dev if cfg.windows else dev)
        g.LOG.write(f"Initialised pycdlib instance successfully...")
        self.dvdcss = DvdCss()
        self.dvdcss.open(dev)
        g.LOG.write(f"Initialised pydvdcss instance successfully...")
        self.ready = True
        g.LOG.write(f"DVD opened and ready...\n")
        if js:
            js.Call()

    def is_ready(self, js):
        """
        Simple function just to be able to check if this Dvd
        instance is ready to be used for reading and what not.

        Cefpython cannot export the Properties of Dvd, so this
        is the next best way of doing it.
        """
        js.Call(self.ready)

    @asynchronous_auto
    def compute_crc_id(self, js=None):
        """
        Get the CRC64 checksum known as the Media Player DVD ID.
        The algorithm used is the exact same one used by Microsoft's old Windows Media Center.
        """
        crc = str(rlapydvdid.compute(self.dev))
        g.LOG.write(f"Got CRC64 DVD ID: {crc}\n")
        if js:
            js.Call(crc)
        return crc

    @asynchronous_auto
    def get_primary_descriptor(self, js=None):
        """
        Get's and returns the Primary Volume Descriptor of the
        disc in a more accessible and parsed format.
        """
        pvd = self.cdlib.pvds[0]

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

        pvd = {
            "version": pvd.version,
            "version_fs": pvd.file_structure_version,
            "flags": pvd.flags,
            "sector_size": pvd.log_block_size,
            "total_sectors": pvd.space_size,
            "size": pvd.log_block_size * pvd.space_size,
            "system_id": pvd.system_identifier.decode().strip() or None,
            "volume_id": pvd.volume_identifier.decode().strip() or None,
            "volume_set_id": pvd.volume_set_identifier.decode().strip() or None,
            "publisher_id": pvd.publisher_identifier.record().decode().strip() or None,
            "preparer_id": pvd.preparer_identifier.record().decode().strip() or None,
            "application_id": pvd.application_identifier.record().decode().strip() or None,
            "copyright_file_id": pvd.copyright_file_identifier.decode().strip() or None,
            "abstract_file_id": pvd.abstract_file_identifier.decode().strip() or None,
            "bibliographic_file_id": pvd.bibliographic_file_identifier.decode().strip() or None,
            "creation_date": date_convert(pvd.volume_creation_date),
            "expiration_date": date_convert(pvd.volume_expiration_date),
            "effective_date": date_convert(pvd.volume_effective_date),
            "escape_seq": f"00 * {len(pvd.escape_sequences)}" if pvd.escape_sequences == bytearray(
                len(pvd.escape_sequences)) else pvd.escape_sequences,
            "set_size": pvd.set_size,
            "seq_num": pvd.seqnum,
            "path_tbl_size": pvd.path_tbl_size,
            "path_table_location_le": pvd.path_table_location_le,
            "path_table_location_be": pvd.path_table_location_be,
            "optional_path_table_location_le": pvd.optional_path_table_location_le,
            "optional_path_table_location_be": pvd.optional_path_table_location_be,
            "application_reserve": None if pvd.application_use == bytearray(512) else pvd.application_use
        }
        g.LOG.write(f"Got Primary Volume Descriptor: {pvd}\n")
        if js:
            # cefpython complaints it's too big for an `int`
            pvd["size"] = str(pvd["size"])
            js.Call(pvd)
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
            g.LOG.write(f"Found title file: {file_path}, lba: {lba}, size: {size}")
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
                    g.LOG.write(f"Got title key for {vob}")
                else:
                    raise SlipstreamSeekError(
                        f"Failed to seek the disc to {lba} while attempting to "
                        f"crack the title key for {os.path.basename(vob)}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Return lba data
        return lba_data

    @asynchronous_auto
    def create_backup(self, js=None):
        """
        Create a full untouched (but decrypted) ISO backup of a DVD with all
        metadata intact.

        Raises SlipstreamNoKeysObtained if no CSS keys were obtained when needed.
        Raises SlipstreamReadError on unexpected read errors.
        """
        try:
            # Notify JS-land we're starting
            if js:
                js.Call(True)
            # Print primary volume descriptor information
            g.LOG.write(f"Starting DVD backup for {self.dev}")
            pvd = self.cdlib.pvds[0]
            pvd.volume_identifier = pvd.volume_identifier.decode().strip()
            fn = f"{pvd.volume_identifier}.ISO"
            fn_tmp = f"{pvd.volume_identifier}.ISO.tmp"
            first_lba = 0
            last_lba = pvd.space_size - 1
            disc_size = pvd.space_size * self.dvdcss.SECTOR_SIZE
            g.LOG.write(
                f"Reading sectors {first_lba:,} to {last_lba:,} with sector size {self.dvdcss.SECTOR_SIZE:,} B.\n"
                f"Length: {last_lba + 1:,} sectors, {disc_size:,} bytes.\n"
                f'Saving to "{fn}"...'
            )
            # Retrieve CSS keys if disc is scrambled
            if self.dvdcss.is_scrambled():
                g.LOG.write("DVD is scrambled. Checking if all CSS keys can be cracked. This might take a while.")
                self.vob_lba_offsets = self.get_vob_lbas(crack_keys=True)
                if not self.vob_lba_offsets:
                    raise SlipstreamNoKeysObtained("No CSS title keys were returned, unable to decrypt.")
            else:
                g.LOG.write("DVD isn't scrambled. CSS title key cracking skipped.")
            # Create a file write handle to temp file
            f = open(fn_tmp, "wb")
            # Create a TQDM progress bar
            t = tqdm(total=last_lba + 1, unit="sectors", file=TqdmHook())
            # Read through all the sectors in a memory efficient manner
            current_lba = first_lba
            g.LOG.write(f"Reading sectors {current_lba}->{last_lba}...")
            while current_lba <= last_lba:
                # get the maximum sectors to read at once
                sectors = min(self.dvdcss.BLOCK_BUFFER, last_lba - current_lba + 1)
                # read sectors
                read_sectors = self.read(current_lba, sectors)
                if read_sectors < 0:
                    raise SlipstreamReadError(f"An unexpected read error occurred reading {current_lba}->{sectors}")
                # write the buffer to output file
                f.write(self.dvdcss.buffer)
                # increment the current sector and update the tqdm progress bar
                current_lba += read_sectors
                # write progress to GUI log
                g.PROGRESS.c.Call((current_lba / last_lba) * 100)
                # write progress to CLI log
                t.update(read_sectors)
            # Close file and tqdm progress bar
            f.close()
            t.close()
            # Rename temp file to final filename
            os.rename(fn_tmp, fn)
            # Tell the user some output information
            g.LOG.write(
                "Finished DVD Backup!\n"
                f"Read a total of {current_lba:,} sectors ({os.path.getsize(fn):,}) bytes.\n"
            )
        finally:
            # Notify js-land were done
            if js:
                js.Call(False)

    def read(self, first_lba, sectors):
        """
        Efficiently read an amount of sectors from the disc while supporting decryption
        with libdvdcss (pydvdcss).

        Returns the amount of sectors read.
        Raises a SlipstreamSeekError on Seek Failures and SlipstreamReadError on Read Failures.
        """

        # we need to seek to the first sector. Otherwise we get faulty data.
        needToSeek = first_lba != self.reader_position or first_lba == 0
        inTitle = False
        enteredTitle = False

        # Make sure we never read encrypted and unencrypted data at once since libdvdcss
        # only decrypts the whole area of read sectors or nothing at all.
        for vob_lba_offset in self.vob_lba_offsets:
            titleStart = vob_lba_offset[0]
            titleEnd = titleStart + vob_lba_offset[1] - 1

            # update key when entering a new title
            # FIXME: we also need this if we seek into a new title (not only the start of the title)
            if titleStart == first_lba:
                enteredTitle = needToSeek = inTitle = True

            # if first_lba < titleStart and first_lba + sectors > titleStart:
            if first_lba < titleStart < first_lba + sectors:
                # read range will read beyond or on a title,
                # let's read up to right before the next title start
                sectors = titleStart - first_lba

            # if first_lba < titleEnd and first_lba + sectors > titleEnd:
            if first_lba < titleEnd < first_lba + sectors:
                # read range will read beyond or on a title,
                # let's read up to right before the next title start
                sectors = titleEnd - first_lba + 1

            # is our read range part of one title
            if first_lba >= titleStart and first_lba + (sectors - 1) <= titleEnd:
                inTitle = True

        if needToSeek:
            flags = self.dvdcss.NOFLAGS
            if enteredTitle:
                flags = self.dvdcss.SEEK_KEY
            elif inTitle:
                flags = self.dvdcss.SEEK_MPEG

            # refresh the key status for this sector's data
            self.reader_position = self.dvdcss.seek(first_lba, flags)
            if self.reader_position != first_lba:
                raise SlipstreamSeekError(f"Failed to seek the disc to {first_lba} while doing a device read.")

        flags = self.dvdcss.NOFLAGS
        if inTitle:
            flags = self.dvdcss.READ_DECRYPT

        ret = self.dvdcss.read(sectors, flags)
        if ret != sectors:
            raise SlipstreamReadError(f"An unexpected read error occurred reading {first_lba}->{first_lba + sectors}")
        self.reader_position += ret

        return ret


class TqdmHook:
    """hook to simply intercept tqdm's progress messages and log them."""

    @staticmethod
    def write(text):
        # log the tqdm progress message
        g.LOG.write(text, echo=False)
        # return it to stdout
        return sys.stdout.write(text)

    @staticmethod
    def flush():
        # return it to stdout, we don't need to flush the log
        sys.stdout.flush()
