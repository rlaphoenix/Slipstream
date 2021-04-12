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
import logging

from pycdlib import PyCdlib


def get_volume_id(device):
    """
    Get the Volume Identifier for a device

    Returns None if there's no disc inserted
    """
    log = logging.getLogger("cdlib")
    cdlib = PyCdlib()
    try:
        cdlib.open(device, "rb")
    except OSError as e:
        # noinspection SpellCheckingInspection
        if "[Errno 123]" in str(e):
            # no disc inserted
            log.info(f"Device {device} has no disc inserted.")
            return None
        # noinspection SpellCheckingInspection
        if "[Errno 5]" in str(e):
            # Input/output error
            log.error(f"Device {device} had an I/O error.")
            return "! Error occurred reading disc..."
        raise
    volume_id = cdlib.pvds[0].volume_identifier.decode().strip()
    log.info(f"Device {device} has disc labeled \"{volume_id}\".")
    return volume_id
