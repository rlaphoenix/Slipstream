# std
import os
# pip packages
from pydvdcss import PyDvdCss
from tqdm import tqdm
import pycdlib
import pydvdid


class Dvd:
    def __init__(self):
        self.dev = None
        self.cdlib = None
        self.dvdcss = None
        self.reader_position = 0
        self.vob_lba_offsets = []
        self.crcid = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.dispose()
    
    def dispose(self):
        if self.cdlib:
            self.cdlib.close()
        if self.dvdcss:
            self.dvdcss.dispose()
        self.__init__()  # reset everything

    def open(self, dev):
        if self.dvdcss or self.cdlib:
            raise ValueError("Slipstream.Dvd: A disc has already been opened.")
        self.dev = dev
        self.cdlib = pycdlib.PyCdlib()
        self.cdlib.open(dev)
        self.dvdcss = PyDvdCss()
        self.dvdcss.open(dev)
        self.print_primary_descriptor()
        # get disc crc id (aka DVD Id)
        self.crcid = str(pydvdid.compute(dev))
        print(f"DVD CRC ID (aka DVD ID): {self.crcid}\n")
    
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
        Raises an IOError on seek failures.
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
                    raise IOError(
                        f"Slipstream.Dvd.get_vob_lbas: Failed to crack title key for {os.path.basename(vob)} at sector {lba}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Return lba data
        return lba_data

    def create_backup(self):
        """
        Create a full untouched (but decrypted) ISO backup of a DVD with all
        metadata intact.
        Raises an IOError on read or key cracking failures.
        """
        # Print primary volume descriptor information
        pvd = self.cdlib.pvds[0]
        pvd.volume_identifier = pvd.volume_identifier.decode().strip()
        fn = f"{pvd.volume_identifier}.ISO"
        fn_tmp = f"{pvd.volume_identifier}.ISO.tmp"
        first_lba = 0
        last_lba = pvd.space_size - 1
        disc_size = pvd.space_size * self.dvdcss.SECTOR_SIZE
        print(
            f"Reading sectors {first_lba:,} to {last_lba:,} with sector size {self.dvdcss.SECTOR_SIZE:,} B.\n"
            f"Length: {last_lba + 1:,} sectors, {disc_size:,} bytes.\n"
            f'Saving to "{fn}"...'
        )
        # Retrieve CSS keys
        print("Checking if all CSS keys can be cracked. This might take a while.")
        try:
            self.vob_lba_offsets = self.get_vob_lbas(crack_keys=True)
        except IOError as e:
            raise IOError(str(e) + "\nSlipstream.Dvd.create_backup: Failed to retrive a CSS key, backup cannot continue.")
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
                raise IOError("Slipstream.Dvd.create_backup: An unexpected read error occured.")
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
            "Finished DVD Backup!",
            f"Read a total of {current_lba:,} sectors ({os.path.getsize(fn):,}) bytes."
        )
    
    def read(self, first_lba, sectors):
        """
        Efficiently read an amount of sectors from the disc while supporting decryption
        with libdvdcss (pydvdcss).

        Returns the amount of sectors read.
        Raises an IOError on read or seek failures.
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

            # update key when entrering a new title
            # FIXME: we also need this if we seek into a new title (not only the start of the title)
            if titleStart == first_lba:
                enteredTitle = needToSeek = inTitle = True

            if first_lba < titleStart and first_lba + sectors > titleStart:
                # read range will read beyond or on a title,
                # let's read up to right before the next title start
                sectors = titleStart - first_lba

            if first_lba < titleEnd and first_lba + sectors > titleEnd:
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
                raise IOError(f"Slipstream.Dvd.read: seek to {first_lba} failed, it seeked to {self.reader_position}")

        flags = self.dvdcss.NOFLAGS
        if inTitle:
            flags = self.dvdcss.READ_DECRYPT

        ret = self.dvdcss.read(sectors, flags)
        if ret != sectors:
            raise IOError(f"Slipstream.Dvd.read: unexpected read failure for {first_lba}-{first_lba+sectors}")
        self.reader_position += ret

        return ret
