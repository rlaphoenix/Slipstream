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
import sys
from ctypes import wintypes
from typing import Optional

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


class ScsiReader:
    """
    Persistent raw SCSI (SPTI) sector reader for an optical device. Windows-only.

    Opens the device once with write access (required for pass-through; no admin needed) and serves
    SCSI READ(12) commands, splitting large reads into drive-sized chunks.
    """

    def __init__(self, device_path: str) -> None:
        self._handle: Optional[int] = None
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
            chunk = min(_MAX_SCSI_SECTORS, count - offset)
            data = _scsi_read12(self._k32, self._handle, lba + offset, chunk)
            if data is None or len(data) != chunk * SECTOR_SIZE:
                return None
            out += data
            offset += chunk
        return bytes(out)

    def close(self) -> None:
        if self._handle is not None:
            self._k32.CloseHandle(self._handle)
            self._handle = None
