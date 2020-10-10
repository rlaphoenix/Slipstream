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

import argparse
import builtins as g
import hashlib
import os
import webbrowser

import requests
from appdirs import user_data_dir

from cefpython3 import cefpython as cef

import pslipstream.cfg as cfg
from pslipstream.config import Config
from pslipstream.dvd import Dvd
from pslipstream.gui import Gui
from pslipstream.helpers import get_device_list
from pslipstream.log import Log
from pslipstream.progress import Progress


def main():
    # Prepare Metadata
    cfg.cef_version = cef.GetVersion()
    cfg.user_dir = user_data_dir(cfg.title_pkg, cfg.author)
    cfg.config_file = os.path.join(cfg.user_dir, "config.yml")

    # Initialize custom global variables
    g.ARGS = get_arguments()
    g.LOG = Log()  # Logger, everything written here gets print()'d and sent to GUI
    g.PROGRESS = Progress()  # Progress Bar, controls only the GUI's progress bar.
    g.DBG = g.ARGS.dbg  # Debug switch, enables debugging specific code and logging
    g.CFG = Config(cfg.config_file)
    g.CFG.load()

    # Print License if asked
    if g.ARGS.license:
        if not os.path.exists("LICENSE"):
            # download the license from the official source if not found locally
            lic_url = "https://www.gnu.org/licenses/gpl-3.0.txt"
            lic_text = requests.get(lic_url).text
            # noinspection SpellCheckingInspection
            expected_md5 = "1ebbd3e34237af26da5dc08a4e440465"
            computed_md5 = hashlib.md5(lic_text.encode("utf-8")).hexdigest()
            if computed_md5 != expected_md5:
                print(
                    "License file was not found locally and it also failed to download :(\n"
                    f"If you would like to read the LICENSE file, head over to {lic_url}"
                )
            else:
                print(lic_text)
        else:
            with open("LICENSE", mode="rt", encoding="utf-8") as f:
                print(f.read())
        exit(0)

    # Get and Print Runtime Details
    g.LOG.write(get_runtime_details() + "\n")

    # Let's get to it
    if g.ARGS.cli:
        cli()
    else:
        gui()


def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dev",
        nargs="*",
        required=False,
        help="This is only to be used by dev's that know what it does!!",
    )
    ap.add_argument(
        "--dbg",
        action="store_true",
        default=False,
        required=False,
        help="Debug mode, may have increased logging that could hurt performance.",
    )
    ap.add_argument(
        "--license",
        action="store_true",
        default=False,
        required=False,
        help="View license details",
    )
    ap.add_argument(
        "--cli",
        action="store_true",
        default=False,
        required=False,
        help="Setting this stops the GUI from running",
    )
    ap.add_argument(
        "-d",
        "--device",
        type=str,
        default="",
        required=False,
        help="Choose device for backup (e.g. '/dev/sr0', '/mnt/dvd-rw', 'E:')",
    )
    return ap.parse_args()


def get_runtime_details():
    return "\n".join(
        [
            cfg.copyright_paragraph,
            "",
            f"{cfg.title} v{cfg.version}",
            cfg.description,
            cfg.url,
            "",
            f":: {'DEBUG' if g.DBG else 'Standard'} MODE",
            f":: {cfg.platform} {cfg.architecture} (Python v{cfg.py_version})",
            f":: CEF Runtime: {cfg.cef_version}",
            f":: User Directory: {cfg.user_dir}",
            f":: Static Directory: {cfg.static_dir}",
        ]
    )


def gui():
    # set ui index location based on environment
    if g.ARGS.dev:
        port = None
        if "ui-build" in g.ARGS.dev:
            # gatsby build && gatsby serve
            port = 9000
        elif "ui-develop" in g.ARGS.dev:
            # gatsby develop
            port = 8000
        cfg.ui_index = "http://localhost:" + str(port)
    else:
        cfg.ui_index = "https://slipstream-ui.vercel.app"
    # create gui, and fire it up
    g.GUI = Gui(
        url=cfg.ui_index,
        icon=cfg.icon_file,
        js_bindings={
            "properties": [
                {"name": "config", "item": g.CFG.settings},
            ],
            "objects": [
                {"name": "dvd", "item": Dvd()},
                {"name": "log", "item": g.LOG},
                {"name": "progress", "item": g.PROGRESS},
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


def cli():
    d = Dvd()
    d.open(g.ARGS.device)
    d.create_backup()


if __name__ == "__main__":
    main()
