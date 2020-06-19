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
import os
import argparse
import builtins as g
import webbrowser
import requests

# slipstream
import slipstream.__version__ as meta
from slipstream.config import Config
from slipstream.gui import Gui
from slipstream.helpers import get_device_list
from slipstream.dvd import Dvd


def main():

    # Parse Arguments
    ArgParser = argparse.ArgumentParser()
    ArgParser.add_argument(
        "--license",
        action="store_true",
        default=False,
        required=False,
        help="View license details",
    )
    ArgParser.add_argument(
        "--dev",
        action="store_true",
        default=False,
        required=False,
        help="This isn't a debug mode, it's mainly for internally switching data based on dev/prod env.",
    )
    ArgParser.add_argument(
        "--cli",
        action="store_true",
        default=False,
        required=False,
        help="Setting this stops the GUI from running",
    )
    ArgParser.add_argument(
        "-d",
        "--device",
        type=str,
        default="",
        required=False,
        help="Choose device for backup (e.g. '/dev/sr0', '/mnt/dvdrw', 'E:')",
    )
    args = ArgParser.parse_args()

    # Initialize custom global variables
    g.LOG = Log()
    g.PROG = Progress()
    g.DBG = False
    g.CFG = Config(meta.__config_file__)
    g.CFG.load()

    # Print License if asked
    if args.license:
        if not os.path.exists("LICENSE"):
            print(requests.get("https://www.gnu.org/licenses/gpl-3.0.txt").text)
        with open("LICENSE", "rt", "utf-8") as f:
            print(f.read())
        exit(0)

    # Get and Print Runtime Details
    g.LOG.write(get_runtime_details() + "\n")
    print(g.LOG.read_all())

    # Let's get to it
    if args.cli:
        CLI_ROUTE(args)
    else:
        GUI_ROUTE(args)


def get_runtime_details():
    return "\n".join(
        [
            meta.__copyright_paragraph__,
            "",
            f"{meta.__title__} v{meta.__version__}",
            meta.__description__,
            meta.__url__,
            "",
            f":: {'DEBUG' if g.DBG else 'Standard'} MODE",
            f":: {meta.__platform__} {meta.__architecture__} (Python v{meta.__py_version__})",
            f":: CEF Runtime: {meta.__cef_version__}",
            f":: User Directory: {meta.__user_dir__}",
            f":: Static Directory: {meta.__static_dir__}",
        ]
    )



def GUI_ROUTE(args):
    # set ui index location based on environment
    if args.dev:
        meta.__ui_index__ = "http://localhost:8000/"
    else:
        meta.__ui_index__ = "https://phoenix-slipstream.netlify.app/"
    # create gui, and fire it up
    g.GUI = Gui(
        url=meta.__ui_index__,
        icon=meta.__icon_file__,
        js_bindings={
            "properties": [
                {"name": "config", "item": g.CFG.settings},
            ],
            "objects": [
                {"name": "dvd", "item": Dvd()},
                {"name": "log", "item": g.LOG},
                {"name": "progress", "item": g.PROG},
            ],
            "functions": [
                {"name": "pyDelete", "item": os.remove},
                {"name": "pyHref", "item": lambda url: webbrowser.open(url)},
                {"name": "configSave", "item": g.CFG.save},
                {"name": "getDeviceList", "item": get_device_list},
            ],
        },
    )
    g.GUI.mainloop()


def CLI_ROUTE(args):

    dvd = Dvd()
    dvd.open(args.device)
    dvd.create_backup()


class Log:
    def __init__(self):
        self.entries = []
        self.js = None
        self.max_entries = 100

    def write(self, entry, echo=True):
        self.entries.append(entry)
        while len(self.entries) > self.max_entries:
            self.entries.pop(0)
        if echo:
            print(entry.strip())
        if self.js:
            # update js log
            self.read_all()
    
    def set_js(self, js):
        self.js = js
        self.read_all()  # get initial log

    def read_all(self, js=None):
        entries = "\n".join(self.entries).strip()
        if self.js:
            self.js.Call(entries)
        return entries

class Progress:
    def __init__(self):
        self.progress = 0
        self.c = None
    
    def set_c(self, js):
        self.c = js


if __name__ == "__main__":
    main()
