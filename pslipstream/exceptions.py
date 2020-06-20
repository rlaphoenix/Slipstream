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

Definitions of Slipstream exceptions.
"""


class TkinterVersionError(Exception):
    """Tkinter version is too outdated, update tkinter to continue."""


class CefInitializationError(Exception):
    """CEF Failed to initialize."""


class WindowHandleError(Exception):
    """Couldn't obtain the GUI's window handle."""


class SlipstreamUiError(Exception):
    """Failed to load the UI."""


class SlipstreamDiscInUse(Exception):
    """A disc is already initialised in this instance."""


class SlipstreamNoKeysObtained(Exception):
    """No keys were returned, unable to decrypt."""


class SlipstreamReadError(Exception):
    """An unexpected read error occurred."""


class SlipstreamSeekError(Exception):
    """An unexpected seek error occurred."""
