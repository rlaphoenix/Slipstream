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
"""

# std
import sys
import tkinter as tk
# pip packages
from cefpython3 import cefpython as cef
# slipstream
import slipstream.__version__ as meta
import slipstream.exceptions as exceptions
from slipstream.gui.browser_frame import BrowserFrame


class Gui(tk.Frame):

    def on_root_configure(self, _):
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        if self.browser_frame:
            width = event.width
            height = event.height
            self.browser_frame.on_mainframe_configure(width, height)

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()
        cef.Shutdown()

    def __init__(self, url, icon, js_bindings=None):
        self.js_bindings = js_bindings
        self.browser_frame = None
        self.master = None
        # Assure Tkinter version is supported
        if tk.TkVersion <= 8.5:
            raise exceptions.TkinterVersionError()
        # tell cef about uncaught exceptions, will shutdown
        sys.excepthook = cef.ExceptHook
        # Create Window
        root = tk.Tk()
        root.geometry(meta.__min_size__)
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)
        tk.Frame.__init__(self, root)
        # Configure Window
        self.master.title(meta.__title__)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        # noinspection PyProtectedMember
        self.master.call(
            "wm",
            "iconphoto",
            self.master._w,
            tk.PhotoImage(file=icon)
        )
        self.bind("<Configure>", self.on_configure)
        # BrowserFrame
        self.browser_frame = BrowserFrame(self, url=url, js_bindings=self.js_bindings)
        self.browser_frame.grid(row=0, column=0, sticky=(tk.N + tk.S + tk.E + tk.W))
        self.browser = self.browser_frame.browser
        self.ui_handler = self.browser_frame.ui_handler
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)
        # Initialize CEF
        if not cef.Initialize(settings={
            "debug": False,
            "command_line_args_disabled": True,
            "context_menu": {  # we use a custom context menu all the time, we cant have both
                "enabled": False,
                "navigation": False,
                "print": False,
                "view_source": False,
                "external_browser": False,
                "devtools": False
            },
            "cache_path": "",  # disable
            "ignore_certificate_errors": False,
            "downloads_enabled": False,
            "locale": "en-US",
            "log_severity": cef.LOGSEVERITY_DISABLE,
            "persist_session_cookies": False,
            "persist_user_preferences": False,
            "remote_debugging_port": -1,
            "product_version": f"Slipstream/{meta.__version__}",  # user agent for the UI
            "background_color": 0xff202225
        }, switches={
            "no-proxy-server": "",  # avoid using ie set proxy, if they want to system-wide proxy, use vpn
            "allow-file-access-from-files": ""  # so we can use locally stored files for includes on main html file
        }):
            raise exceptions.CefInitilizationError()
