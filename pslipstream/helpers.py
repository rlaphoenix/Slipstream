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

Various small simple helper functions to do a quick task while not
being specific enough to be in a class.
"""
import builtins as g
import queue
import subprocess
import threading

import pslipstream.cfg as cfg
from pycdlib import PyCdlib

if cfg.windows:
    from win32 import win32api, win32file


def list_devices():
    """
    Lists all devices provided by lsscsi
    """
    if cfg.windows:
        drives = [
            rf"\\.\{d[:-1]}" for d in win32api.GetLogicalDriveStrings().split('\x00')[:-1]
            if win32file.GetDriveType(d) == win32file.DRIVE_CDROM
        ]
        print(drives)
        drives = [{
            "loc": d,
            "volid": get_volume_id(d)
        } for d in drives]
        return drives
    if cfg.linux:
        lsscsi = subprocess.check_output(["lsscsi"]).decode().splitlines()
        lsscsi = [x[9:].strip() for x in lsscsi]

        lsscsi = [[x for x in scsi.split(" ") if x] for scsi in lsscsi]
        lsscsi = [{
            "type": scsi[0],
            "make": scsi[1],
            "model": " ".join([scsi[2]] if len(scsi) == 5 else scsi[2:(len(scsi) - 2)]),
            "fwver": scsi[-2],
            "loc": scsi[-1],
            "volid": get_volume_id(scsi[-1])
        } for scsi in lsscsi if scsi[0] not in ["disk"]]
        return lsscsi


def get_volume_id(device):
    """
    Get the Volume Identifier for a device

    Returns None if there's no disc inserted
    """
    cdlib = PyCdlib()
    try:
        cdlib.open(device, "rb")
    except OSError as e:
        # noinspection SpellCheckingInspection
        if "[Errno 123]" in str(e):
            # no disc inserted
            g.LOG.write(f"Device {device} has no disc inserted.")
            return None
        # noinspection SpellCheckingInspection
        if "[Errno 5]" in str(e):
            # Input/output error
            g.LOG.write(f"Device {device} had an I/O error.")
            return "! Error occurred reading disc..."
        raise
    volume_id = cdlib.pvds[0].volume_identifier.decode().strip()
    g.LOG.write(f"Device {device} has disc labeled \"{volume_id}\".")
    return volume_id


def get_device_list(js):
    js.Call(sorted(list_devices(), key=lambda d: d["volid"] or "", reverse=True))


def asynchronous(f, daemon=True, auto_start=False):
    def wrapped_f(q, *args, **kwargs):
        """
        this function calls the decorated function and puts the
        result in a queue
        """
        ret = f(*args, **kwargs)
        q.put(ret)

    def wrap(*args, **kwargs):
        """
        this is the function returned from the decorator. It fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached
        """

        q = queue.Queue()

        t = threading.Thread(target=wrapped_f, args=(q,) + args, kwargs=kwargs)
        t.daemon = daemon
        if auto_start:
            t.start()
        t.result_queue = q
        return t

    return wrap


def asynchronous_auto(f):
    return asynchronous(f, auto_start=True)
