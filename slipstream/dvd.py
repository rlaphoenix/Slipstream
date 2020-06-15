# std
import os
import subprocess
import array
import fcntl
import struct
import glob
# pip packages
from pydvdcss import PyDvdCss
# slipstream
from slipstream.helpers import get_mount_path, mount, unmount


class Dvd:
    def __init__(self):
        self.dvdcss = None
        self.dev = None
        self.reader_position = 0
        self.vob_lba_offsets = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.dispose()
    
    def dispose(self):
        if self.dvdcss:
            self.dvdcss.dispose()

    def open(self, dev):
        if self.dvdcss:
            raise ValueError("Slipstream.Dvd: A disc has already been opened.")
        self.dev = dev
        self.dvdcss = PyDvdCss()
        self.dvdcss.open(dev)
    
    def ensure_mount(self):
        """
        Ensure the device is mounted and return the mount path
        Returns a tuple of:
        - Mount path
        - Temp mount (bool)
        """
        mnt = get_mount_path(self.dev)
        tmp_mnt = False
        if not mnt:
            # not yet mounted, mount now
            mnt = mount(self.dev)
            tmp_mnt = True
        return mnt, tmp_mnt

    def get_volume_info(self):
        """
        Read volume information from disc's 16th sector
        Returns a tuple of:
        - Volume Label
        - First Sector LBA
        - Last Sector LBA
        - Disc Size in Bytes
        """
        # Read volume information from sector 16
        self.dvdcss.seek(16)
        read = self.dvdcss.read(1)
        if read != 1:
            raise Exception(
                "Slipstream.Dvd.get_volume_info: Failed to retrieve volume information."
            )
        last_sector = struct.unpack_from("<I", self.dvdcss.buffer, 80)[0] - 1
        return (
            # Volume Label
            self.dvdcss.buffer[40:72].decode().strip(),
            # First Sector LBA
            0,
            # Last Sector LBA
            last_sector,
            # Disc Size in Bytes
            (last_sector + 1) * self.dvdcss.SECTOR_SIZE,
        )
    
    def get_vob_lbas(self, crack_keys=False):
        """
        Get the LBA data for all VOB files in disc.
        Optionally seek with SEEK_KEY flag to obtain keys.
        """
        # Create an array for holding the title data
        lba_data = []
        # Ensure device is mounted to read files
        mnt, tmp_mnt = self.ensure_mount()
        # Loop all VOB files in disc
        for vob in glob.glob(os.path.join(mnt, "VIDEO_TS/*.VOB")):
            # load file's descriptor
            fd = os.open(vob, os.O_RDONLY)
            # get file's lba
            lba = array.array("I", [0])
            fcntl.ioctl(fd, 1, lba, True)
            lba = lba[0]
            # get file's size
            size = os.lseek(fd, 0, os.SEEK_END)
            if size % self.dvdcss.SECTOR_SIZE:
                raise Exception(
                    f"Slipstream.Dvd.get_vob_lbas: Oh no, for some reason {os.path.basename(vob)} isn't divisable by {self.dvdcss.SECTOR_SIZE}"
                )
            size = int(size / self.dvdcss.SECTOR_SIZE)
            # close file descriptor
            os.close(fd)
            # get title key
            if crack_keys:
                print(f"Slipstream.Dvd.get_vob_lbas: Getting title key for {os.path.basename(vob)} at sector {lba}")
                if lba != self.dvdcss.seek(lba, self.dvdcss.SEEK_KEY):
                    raise Exception(
                        f"Slipstream.Dvd.get_vob_lbas: Failed to crack title key for {os.path.basename(vob)} at sector {lba}"
                    )
            # add data to title offsets
            lba_data.append((lba, size))
        # Unmount device if it was temp mounted
        if tmp_mnt:
            unmount(self.dev)
        # Return lba data
        return lba_data

    def create_backup(self):
        # Retrieve volume information
        (volume_label, first_lba, last_lba, disc_size) = self.get_volume_info()
        fn = f"{volume_label}.ISO"
        fn_tmp = f"{volume_label}.tmp"
        print(
            f"{self.dev}: {volume_label}\n"
            f"Reading sectors {first_lba} to {last_lba} with sector size {self.dvdcss.SECTOR_SIZE}.\n"
            f"Length: {last_lba + 1} sectors, {disc_size} bytes.\n"
            f'Saving to "{fn}"...'
        )
        # Retrieve CSS keys
        print("Retrieving CSS title keys. This might take a while.")
        self.vob_lba_offsets = self.get_vob_lbas(crack_keys=True)
        if not self.vob_lba_offsets:
            raise Exception("Slipstream.Dvd.create_backup: Failed to retrive CSS keys.")
        # Create a nifty data-monitor based progress bar that also works as a file write handle
        # todo ; pv is possibly linux only?
        f = subprocess.Popen(
            f"pv -p -e -r -s {disc_size} > {fn_tmp}", shell=True, stdin=subprocess.PIPE
        ).stdin
        # Read through all the sectors in a memory effecient manner
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
            # incremement the current sector
            current_lba += read_sectors
        # Close data-monitor progress bar as we are finished
        f.close()
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
