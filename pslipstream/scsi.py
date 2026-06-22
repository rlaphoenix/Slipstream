"""
Raw optical-disc sector reads via the Windows SCSI Pass-Through Interface (SPTI).

libdvdcss reads a disc through its logical volume, which Windows can declare one or more sectors shorter
than the disc actually is - and it can also fail on a sector the volume path won't serve. A raw SCSI
READ(12) goes straight to the drive over a different path and can reach those sectors. SPTI needs the
device handle opened with write access (read-only is denied), but no administrator elevation.

This returns raw, undecrypted bytes, so it is only used to recover UNSCRAMBLED sectors (outside a CSS
title). A drive will not serve CSS-scrambled sectors over raw SCSI without authentication anyway.
"""

from __future__ import annotations

import ctypes
import logging
import os
import struct
import sys
from ctypes import wintypes
from typing import Optional

log = logging.getLogger("Scsi")

SECTOR_SIZE = 2048
_MAX_SCSI_SECTORS = 32  # split larger reads to stay within drive transfer limits (64 KiB is a safe ceiling)

_IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x4D014
_GENERIC_READ = 0x80000000
_GENERIC_WRITE = 0x40000000
_FILE_SHARE_READ = 0x1
_FILE_SHARE_WRITE = 0x2
_OPEN_EXISTING = 3
_INVALID_HANDLE = ctypes.c_void_p(-1).value

if sys.platform == "win32":

    class _SPTD(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.USHORT),
            ("ScsiStatus", ctypes.c_ubyte),
            ("PathId", ctypes.c_ubyte),
            ("TargetId", ctypes.c_ubyte),
            ("Lun", ctypes.c_ubyte),
            ("CdbLength", ctypes.c_ubyte),
            ("SenseInfoLength", ctypes.c_ubyte),
            ("DataIn", ctypes.c_ubyte),
            ("DataTransferLength", wintypes.ULONG),
            ("TimeOutValue", wintypes.ULONG),
            ("DataBuffer", ctypes.c_void_p),
            ("SenseInfoOffset", wintypes.ULONG),
            ("Cdb", ctypes.c_ubyte * 16),
        ]

    class _SPTDWithSense(ctypes.Structure):
        _fields_ = [("sptd", _SPTD), ("sense", ctypes.c_ubyte * 32)]


def _new_kernel32() -> "ctypes.WinDLL":
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    k32.DeviceIoControl.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.c_void_p,
    ]
    return k32


def _scsi_read12(k32: "ctypes.WinDLL", handle: int, lba: int, count: int) -> Optional[bytes]:
    """Issue a single SCSI READ(12) for `count` sectors at `lba`. None on a non-zero SCSI status."""
    data = ctypes.create_string_buffer(count * SECTOR_SIZE)
    pkt = _SPTDWithSense()
    pkt.sptd.Length = ctypes.sizeof(_SPTD)
    pkt.sptd.CdbLength = 12
    pkt.sptd.SenseInfoLength = 32
    pkt.sptd.DataIn = 1  # SCSI_IOCTL_DATA_IN
    pkt.sptd.DataTransferLength = count * SECTOR_SIZE
    pkt.sptd.TimeOutValue = 30
    pkt.sptd.DataBuffer = ctypes.cast(data, ctypes.c_void_p)
    pkt.sptd.SenseInfoOffset = type(pkt).sense.offset
    cdb = (ctypes.c_ubyte * 16)()
    cdb[0] = 0xA8  # READ(12)
    cdb[2] = (lba >> 24) & 0xFF
    cdb[3] = (lba >> 16) & 0xFF
    cdb[4] = (lba >> 8) & 0xFF
    cdb[5] = lba & 0xFF
    cdb[6] = (count >> 24) & 0xFF
    cdb[7] = (count >> 16) & 0xFF
    cdb[8] = (count >> 8) & 0xFF
    cdb[9] = count & 0xFF
    pkt.sptd.Cdb = cdb
    returned = wintypes.DWORD(0)
    ok = k32.DeviceIoControl(
        handle,
        _IOCTL_SCSI_PASS_THROUGH_DIRECT,
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(returned),
        None,
    )
    if not ok or pkt.sptd.ScsiStatus != 0:
        return None
    return bytes(data.raw)


def _scsi_read_capacity(k32: "ctypes.WinDLL", handle: int) -> Optional[int]:
    """Issue SCSI READ CAPACITY(10) and return the disc's total sector count. None on failure."""
    data = ctypes.create_string_buffer(8)
    pkt = _SPTDWithSense()
    pkt.sptd.Length = ctypes.sizeof(_SPTD)
    pkt.sptd.CdbLength = 10
    pkt.sptd.SenseInfoLength = 32
    pkt.sptd.DataIn = 1  # SCSI_IOCTL_DATA_IN
    pkt.sptd.DataTransferLength = 8
    pkt.sptd.TimeOutValue = 30
    pkt.sptd.DataBuffer = ctypes.cast(data, ctypes.c_void_p)
    pkt.sptd.SenseInfoOffset = type(pkt).sense.offset
    cdb = (ctypes.c_ubyte * 16)()
    cdb[0] = 0x25  # READ CAPACITY(10)
    pkt.sptd.Cdb = cdb
    returned = wintypes.DWORD(0)
    ok = k32.DeviceIoControl(
        handle,
        _IOCTL_SCSI_PASS_THROUGH_DIRECT,
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(returned),
        None,
    )
    if not ok or pkt.sptd.ScsiStatus != 0:
        return None
    # READ CAPACITY(10) returns the LBA of the LAST sector (big-endian), so add one for the count.
    last_lba = struct.unpack(">I", data.raw[:4])[0]
    return last_lba + 1


def _scsi_set_streaming(k32: "ctypes.WinDLL", handle: int, read_kbps: int) -> bool:
    """
    Issue SCSI SET STREAMING (B6h) to request a drive read speed of `read_kbps` KB/s.

    Returns True if the drive accepted the command. Many drives ignore or cap the request -
    notably firmware "riplock" that throttles DVD-Video reads - so a True result is a request,
    not a guarantee of an actual speed change.
    """
    # Performance Descriptor (MMC SET STREAMING), 28 bytes. The rate is Read Size (KB) per Read
    # Time (ms); with Read Time = 1000 ms, Read Size is simply the speed in KB/s. End LBA
    # 0xFFFFFFFF covers the whole disc. Byte 0 flags are 0 (drive may use up to this rate).
    descriptor = struct.pack(
        ">B3xIIIIII",
        0,  # flags
        0,  # Start LBA
        0xFFFFFFFF,  # End LBA (entire disc)
        read_kbps,  # Read Size (KB)
        1000,  # Read Time (ms)
        read_kbps,  # Write Size (KB), mirrored - harmless for read-only use
        1000,  # Write Time (ms)
    )
    buffer = ctypes.create_string_buffer(descriptor, len(descriptor))
    pkt = _SPTDWithSense()
    pkt.sptd.Length = ctypes.sizeof(_SPTD)
    pkt.sptd.CdbLength = 12
    pkt.sptd.SenseInfoLength = 32
    pkt.sptd.DataIn = 0  # SCSI_IOCTL_DATA_OUT
    pkt.sptd.DataTransferLength = len(descriptor)
    pkt.sptd.TimeOutValue = 30
    pkt.sptd.DataBuffer = ctypes.cast(buffer, ctypes.c_void_p)
    pkt.sptd.SenseInfoOffset = type(pkt).sense.offset
    cdb = (ctypes.c_ubyte * 16)()
    cdb[0] = 0xB6  # SET STREAMING
    cdb[9] = (len(descriptor) >> 8) & 0xFF  # Parameter List Length (MSB)
    cdb[10] = len(descriptor) & 0xFF  # Parameter List Length (LSB)
    pkt.sptd.Cdb = cdb
    returned = wintypes.DWORD(0)
    ok = k32.DeviceIoControl(
        handle,
        _IOCTL_SCSI_PASS_THROUGH_DIRECT,
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(pkt),
        ctypes.sizeof(pkt),
        ctypes.byref(returned),
        None,
    )
    return bool(ok) and pkt.sptd.ScsiStatus == 0


class ScsiReader:
    """
    Persistent raw SCSI (SPTI) sector reader for an optical device. Windows-only.

    Opens the device once with write access (required for pass-through; no admin needed) and serves
    SCSI READ(12) commands, splitting large reads into drive-sized chunks.
    """

    def __init__(self, device_path: str, max_transfer_sectors: int = _MAX_SCSI_SECTORS) -> None:
        self._handle: Optional[int] = None
        self._max_transfer = max(1, max_transfer_sectors)
        if sys.platform != "win32":
            raise OSError("ScsiReader is only supported on Windows")
        self._k32 = _new_kernel32()
        handle = self._k32.CreateFileW(
            device_path,
            _GENERIC_READ | _GENERIC_WRITE,  # write access is required for SPTI; read-only is denied
            _FILE_SHARE_READ | _FILE_SHARE_WRITE,
            None,
            _OPEN_EXISTING,
            0,
            None,
        )
        if handle == _INVALID_HANDLE:
            raise OSError(f"ScsiReader: cannot open {device_path!r} (error {ctypes.get_last_error()})")
        self._handle = handle

    def read(self, lba: int, count: int) -> Optional[bytes]:
        """Read `count` sectors at `lba`, splitting into drive-sized chunks. None on failure."""
        if self._handle is None or count <= 0:
            return None
        out = bytearray()
        offset = 0
        while offset < count:
            chunk = min(self._max_transfer, count - offset)
            data = _scsi_read12(self._k32, self._handle, lba + offset, chunk)
            if data is None or len(data) != chunk * SECTOR_SIZE:
                return None
            out += data
            offset += chunk
        return bytes(out)

    def capacity(self) -> Optional[int]:
        """Return the disc's total sector count via SCSI READ CAPACITY(10). None on failure."""
        if self._handle is None:
            return None
        return _scsi_read_capacity(self._k32, self._handle)

    def set_read_speed(self, read_kbps: int) -> bool:
        """
        Request a drive read speed in KB/s via SCSI SET STREAMING. Returns False if not applied.

        The setting is drive-wide, so it also governs libdvdcss's reads of the same drive. Drives
        may ignore or cap it (e.g. firmware riplock on DVD-Video), so a True result means the
        command was accepted, not that the speed actually changed.
        """
        if self._handle is None or read_kbps <= 0:
            return False
        return _scsi_set_streaming(self._k32, self._handle, read_kbps)

    def close(self) -> None:
        if self._handle is not None:
            self._k32.CloseHandle(self._handle)
            self._handle = None


class ScsiSectorStream:
    """
    A minimal seekable, read-only binary stream over a ScsiReader.

    pycdlib normally reads the device itself, but on Windows its ReadFile path refuses to serve some
    sectors of a CSS-protected DVD with a copy-protection error, which aborts disc parsing. Pointing
    pycdlib at this stream instead routes those reads through raw SCSI, which bypasses that check.
    Byte-range reads are mapped onto sector-aligned SCSI reads and sliced. The bytes are raw and
    undecrypted, which is fine because pycdlib only parses the unscrambled UDF/ISO volume, directory,
    and .IFO structures - never the scrambled VOB title content.

    It exposes a binary ``mode`` and deliberately no ``name``, so pycdlib uses it directly rather than
    wrapping it in its own ``\\\\.\\`` raw-device reader (which would reintroduce the ReadFile path).

    The underlying ScsiReader is owned by the caller, so closing this stream does not close it.
    """

    mode = "rb"

    def __init__(self, reader: ScsiReader, total_sectors: int) -> None:
        self._reader = reader
        self._size = total_sectors * SECTOR_SIZE
        self._pos = 0

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def __len__(self) -> int:
        return self._size

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            pos = offset
        elif whence == os.SEEK_CUR:
            pos = self._pos + offset
        elif whence == os.SEEK_END:
            pos = self._size + offset
        else:
            raise ValueError(f"Invalid whence: {whence}")
        if pos < 0:
            raise OSError("Negative seek position")
        self._pos = pos
        return self._pos

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = max(0, self._size - self._pos)
        size = min(size, max(0, self._size - self._pos))
        if size == 0:
            return b""
        start = self._pos
        start_lba = start // SECTOR_SIZE
        end_lba = -(-(start + size) // SECTOR_SIZE)  # ceil division to cover the final partial sector
        count = end_lba - start_lba
        data = self._reader.read(start_lba, count)
        if data is None:
            # One or more sectors in the range could not be read - commonly the unreadable
            # tail-padding sectors a drive declares but won't serve. pycdlib probes such sectors
            # (e.g. anchor candidates at the physical end) expecting bytes back, not an exception,
            # so recover sector-by-sector and zero-fill the ones that fail (matching how pycdlib's
            # own raw-device reader behaves). Parsing only touches unscrambled structures, so a
            # genuinely needed sector reads fine; a zero-filled one simply fails to parse and is
            # skipped.
            data = self._read_tolerant(start_lba, count)
        inner = start - start_lba * SECTOR_SIZE
        chunk = data[inner : inner + size]
        self._pos += len(chunk)
        return chunk

    def _read_tolerant(self, start_lba: int, count: int) -> bytes:
        """Read each sector individually, substituting a zero-filled sector for any that fail."""
        out = bytearray()
        for lba in range(start_lba, start_lba + count):
            sector = self._reader.read(lba, 1)
            if sector is None:
                log.warning("Sector %d unreadable; zero-filling it for parsing.", lba)
                sector = b"\x00" * SECTOR_SIZE
            out += sector
        return bytes(out)

    def close(self) -> None:
        # The ScsiReader is owned by the caller (Dvd), so it is intentionally not closed here.
        pass
