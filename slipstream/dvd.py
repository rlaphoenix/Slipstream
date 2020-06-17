# std
import os
import datetime
import array
import fcntl
import struct
import glob
# pip packages
from pydvdcss import PyDvdCss
from tqdm import tqdm
import pycdlib


class Dvd:
    def __init__(self):
        self.dev = None
        self.cdlib = None
        self.dvdcss = None
        self.reader_position = 0
        self.vob_lba_offsets = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.dispose()
    
    def dispose(self):
        if self.cdlib:
            self.cdlib.close()
        if self.dvdcss:
            self.dvdcss.dispose()

    def open(self, dev):
        if self.dvdcss or self.cdlib:
            raise ValueError("Slipstream.Dvd: A disc has already been opened.")
        self.dev = dev
        self.cdlib = pycdlib.PyCdlib()
        self.cdlib.open(dev)
        self.dvdcss = PyDvdCss()
        self.dvdcss.open(dev)
        self.print_primary_descriptor()
    
    def print_primary_descriptor(self):
        pvd = self.cdlib.pvds[0]
        print(
            f"\nPrimary Volume Descriptor of `{self.dev}`:\n" +
            "  " + ("\n  ".join([
                f"Version: {pvd.version} [file-structure-ver: {pvd.file_structure_version}]",
                f"Flags: {pvd.flags}",
                f"Sector Size: {pvd.log_block_size}",
                f"Total Sectors: {pvd.space_size}",
                f"Size: {pvd.log_block_size:,} B * {pvd.space_size:,} blocks = {(pvd.log_block_size * pvd.space_size):,}",
                f"System Identifier: {pvd.system_identifier.decode().strip() or '-'}",
                f"Volume Identifier: {pvd.volume_identifier.decode().strip() or '-'}",
                f"Volume Set Identifier: {pvd.volume_set_identifier.decode().strip() or '-'}",
                f"Publisher Identifier: {pvd.publisher_identifier.record().decode().strip() or '-'}",
                f"Preparer Identifier: {pvd.preparer_identifier.record().decode().strip() or '-'}",
                f"Application Identifier: {pvd.application_identifier.record().decode().strip() or '-'}",
                f"Copyright File Identifier: {pvd.copyright_file_identifier.decode().strip() or '-'}",
                f"Abstract File Identifier: {pvd.abstract_file_identifier.decode().strip() or '-'}",
                f"Bibliographic File Identifier: {pvd.bibliographic_file_identifier.decode().strip() or '-'}",
                "\n  ".join([
                    (f"Volume {n} Date: {str(d.year).zfill(4)}-{str(d.month).zfill(2)}-{str(d.dayofmonth).zfill(2)} " +
                    f"{str(d.hour).zfill(2)}:{str(d.minute).zfill(2)}:{str(d.second).zfill(2)}.{d.hundredthsofsecond}" +
                    " GMT+{d.gmtoffset}") for n, d in [
                        ("Creation", pvd.volume_creation_date),
                        ("Expiration", pvd.volume_expiration_date),
                        ("Effective", pvd.volume_effective_date)
                    ]
                ]),
                f"Escape Sequences: {pvd.escape_sequences}",
                f"Set Size: {pvd.set_size}",
                f"Sequence Number: {pvd.seqnum}",
                f"Path Table Size: {pvd.path_tbl_size}",
                f"Path Table Location (little-endian): {pvd.path_table_location_le}",
                f"Path Table Location (big-endian): {pvd.path_table_location_be}",
                f"Path Table Location [opt] (little-endian): {pvd.optional_path_table_location_le}",
                f"Path Table Location [opt] (big-endian): {pvd.optional_path_table_location_be}",
                f"Reserved for Application: {'--' if pvd.application_use == bytearray(512) else pvd.application_use}"
            ])) + "\n"
        )
    
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
            # skip the `.` and `..` paths, we cont care.
            if file_path in [".", ".."]:
                continue
            # remove the semicolon and version number, we dont care.
            if no_versions and ";" in file_path:
                file_path = file_path.split(";")[0]
            # join it to root to be absolute
            file_path = os.path.join("/", path, file_path)
            # get lba
            lba = child.extent_location()
            # get size in sectors
            size = int(child.get_data_length() / self.dvdcss.SECTOR_SIZE)
            yield file_path, lba, size
    
    def get_vob_lbas(self, crack_keys=False):
        """
        Get the LBA data for all VOB files in disc.
        Optionally seek with SEEK_KEY flag to obtain keys.
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
                print(f"Slipstream.Dvd.get_vob_lbas: Getting title key for {os.path.basename(vob)} at sector {lba}")
                if lba != self.dvdcss.seek(lba, self.dvdcss.SEEK_KEY):
                    raise Exception(
                        f"Slipstream.Dvd.get_vob_lbas: Failed to crack title key for {os.path.basename(vob)} at sector {lba}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Return lba data
        return lba_data

    def create_backup(self):
        # Print primary volume descriptor information
        pvd = self.cdlib.pvds[0]
        pvd.volume_identifier = pvd.volume_identifier.decode().strip()
        fn = f"{pvd.volume_identifier}.ISO"
        fn_tmp = f"{pvd.volume_identifier}.tmp"
        first_lba = 0
        last_lba = pvd.space_size
        disc_size = pvd.space_size * self.dvdcss.SECTOR_SIZE
        print(
            f"Reading sectors {first_lba} to {last_lba} with sector size {self.dvdcss.SECTOR_SIZE}.\n"
            f"Length: {last_lba + 1} sectors, {disc_size} bytes.\n"
            f'Saving to "{fn}"...'
        )
        # Retrieve CSS keys
        print("Retrieving CSS title keys. This might take a while.")
        self.vob_lba_offsets = self.get_vob_lbas(crack_keys=True)
        if not self.vob_lba_offsets:
            raise Exception("Slipstream.Dvd.create_backup: Failed to retrive CSS keys.")
        # Create a file write handle to temp file
        f = open(fn_tmp, "wb")
        # Create a TQDM progress bar
        t = tqdm(total=last_lba+1, unit="sectors")
        # Read through all the sectors in a memory efficient manner
        current_lba = first_lba
        while current_lba <= last_lba:
            # get the maximum sectors to read at once
            sectors = min(self.dvdcss.BLOCK_BUFFER, last_lba - current_lba + 1)
            # read sectors
            read_sectors = self.read(current_lba, sectors)
            if read_sectors < 0:
                raise Exception("Slipstream.Dvd.create_backup: An unexpected read error occured.")
            # write the buffer to output file
            f.write(self.dvdcss.buffer)
            # incremement the current sector and update TQDM progress bar
            current_lba += read_sectors
            t.update(read_sectors)
        # Close TQDM progress bar
        f.close()
        t.close()
        # Rename temp file to final filename
        os.rename(fn_tmp, fn)
        # Tell the user some output information
        print(
            "Finished!",
            f"Read a total of {current_lba} sectors ({os.path.getsize(fn)}) bytes."
        )
    
    def read(self, first_lba, sectors):
        """
        Efficiently read an amount of sectors from the disc while supporting decryption
        with libdvdcss (pydvdcss).

        Returns the amount of sectors read
        """

        # we need to seek to the first sector. Otherwise we get faulty data.
        needToSeek = first_lba != self.reader_position or first_lba == 0
        inTitle = 0
        enteredTitle = False

        # Make sure we never read encrypted and unencrypted data at once since libdvdcss
        # only decrypts the whole area of read sectors or nothing at all.
        for vob_lba_offset in self.vob_lba_offsets:
            # [(304, 85386)[end: 85690], (85747, 3211)[end: 88958], (88958, 1349456), (1438457, 5), (1438462, 9790), (1448270, 54), (1448324, 5), (1448356, 5), (1448361, 479524)]
            titleStart = vob_lba_offset[0]
            titleEnd = titleStart + vob_lba_offset[1] - 1

            # update key when entrering a new title
            # FIXME: we also need this if we seek into a new title (not only the start of the title)
            if titleStart == first_lba:
                enteredTitle = needToSeek = inTitle = 1

            if first_lba < titleStart and first_lba + sectors > titleStart:
                print(
                    f"(Slipstream::test) oh no, this read range will read past a title! ({first_lba}-{first_lba + (sectors - 1)}).",
                    f"Instead of reading {sectors} sectors, let's read {titleStart - first_lba} sectors to read up to sector {titleStart - 1}.",
                    f"The next read session should then read from sector {titleStart} :D",
                )
                sectors = titleStart - first_lba

            if first_lba < titleEnd and first_lba + sectors > titleEnd:
                print(
                    f"(Slipstream::test) oh no, this read range will read past a title! ({first_lba}-{first_lba + (sectors - 1)}).",
                    f"Instead of reading {sectors} sectors, let's read {titleEnd - first_lba + 1} sectors to read up to sector {titleEnd}.",
                )
                sectors = titleEnd - first_lba + 1

            # is our read range part of one title
            if first_lba >= titleStart and first_lba + (sectors - 1) <= titleEnd:
                inTitle = (
                    f"The sector range is within a title range ({titleStart}-{titleEnd})"
                )

        if needToSeek:
            flags = self.dvdcss.NOFLAGS
            if enteredTitle:
                flags = self.dvdcss.SEEK_KEY
            elif inTitle:
                flags = self.dvdcss.SEEK_MPEG

            print(
                f"(Slipstream::test) need to seek from {self.reader_position} to {first_lba} with {self.dvdcss.flags_s[flags]}"
            )

            self.reader_position = self.dvdcss.seek(first_lba, flags)
            if self.reader_position != first_lba:
                raise Exception(f"(Slipstream::test) seek to {first_lba} failed: {self.reader_position}")

        flags = self.dvdcss.NOFLAGS
        if inTitle:
            flags = self.dvdcss.READ_DECRYPT

        ret = self.dvdcss.read(sectors, flags)
        if ret != sectors:
            raise Exception(f"(Slipstream::test) unexpected read failure for {first_lba}-{first_lba+sectors}")
        self.reader_position += ret

        return ret
