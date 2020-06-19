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
import hashlib

# slipstream
import pslipstream.__version__ as meta
from pslipstream.config import Config
from pslipstream.gui import Gui
from pslipstream.helpers import get_device_list
from pslipstream.dvd import Dvd


def main():

    # Parse Arguments
    ArgParser = argparse.ArgumentParser()
    ArgParser.add_argument(
        "--dev",
        nargs="*",
        required=False,
        help="This isn't a debug mode, it's mainly for internally switching data, don't use this unless you know what they do!!",
    )
    ArgParser.add_argument(
        "--dbg",
        action="store_true",
        default=False,
        required=False,
        help="Debug mode, may have increased logging that could hurt performance, don't enable unless you debugging.",
    )
    ArgParser.add_argument(
        "--license",
        action="store_true",
        default=False,
        required=False,
        help="View license details",
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
    # These need to be global to be accessed more easily
    # throughout the code, otherwise id have to deal with messy
    # imports and/or passing it from function to function
    g.LOG = Log()  # Logger, everything written here gets print()'d and sent to GUI
    g.PROG = Progress()  # Progress Bar, controls only the GUI's progress bar
    g.DBG = args.dbg  # Debug switch, enables debugging specific code and logging
    g.CFG = Config(meta.__config_file__)
    g.CFG.load()

    # Print License if asked
    if args.license:
        if not os.path.exists("LICENSE"):
            # download the license from the official source if not found locally
            md5 = hashlib.md5()
            lic_url = "https://www.gnu.org/licenses/gpl-3.0.txt"
            lic = requests.get(lic_url).text
            md5.update(lic.encode("utf-8"))
            if md5.hexdigest() != "1ebbd3e34237af26da5dc08a4e440465":
                # this is just to ensure that the license file content doesn't change or
                # fail to download or get re-routed or mitm'd e.t.c. It's important for a
                # license to display correctly!
                print(
                    "License file was not found locally (pesky redistributors! >:L), but "
                    "it also failed to download :(\nIf you would like to read the LICENSE"
                    f", more information can be found here: {lic_url}"
                )
            else:
                print(lic)
        else:
            with open("LICENSE", mode="rt", encoding="utf-8") as f:
                print(f.read())
        exit(0)

    # Get and Print Runtime Details
    g.LOG.write(get_runtime_details() + "\n")

    # Let's get to it
    (CLI_ROUTE if args.cli else GUI_ROUTE)(args)


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
        port = None
        if "ui-build" in args.dev:
            # gatsby build && gatsby serve
            port = 9000
        elif "ui-develop" in args.dev:
            # gatsby develop
            port = 8000
        meta.__ui_index__ = f"http://localhost:{port}/"
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
