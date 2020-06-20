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
try:
    from cefpython3 import cefpython as cef
except Exception as e:
    if str(e).startswith("Python version not supported: 3.8"):
        import site
        raise ImportError(
            "Oh no, cefpython is *still* not supporting 3.8 officially!! >:((\n"
            f"Not to worry, just open '{site.getsitepackages()[0]}/cefpython3/__init__.py' and "
            "change `elif sys.version_info[:2] == (3, 7):` (near ln60) to "
            "`elif sys.version_info[:2] in [(3, 7), (3, 8)]:`\n"
            "Once done, it will work fine on Python 3.8 :)"
        )
    raise

import meta
from pslipstream.config import Config
from pslipstream.dvd import Dvd
from pslipstream.gui import Gui
from pslipstream.helpers import get_device_list
from pslipstream.log import Log
from pslipstream.progress import Progress


def main():
    # Initialize custom global variables
    g.ARGS = get_arguments()
    g.LOG = Log()  # Logger, everything written here gets print()'d and sent to GUI
    g.PROGRESS = Progress()  # Progress Bar, controls only the GUI's progress bar.
    g.DBG = g.ARGS.dbg  # Debug switch, enables debugging specific code and logging
    g.CFG = Config(meta.__config_file__)
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

    # Prepare Metadata
    meta.__cef_version__ = cef.GetVersion()
    meta.__user_dir__ = user_data_dir(meta.__title_pkg__, meta.__author__)
    meta.__config_file__ = os.path.join(meta.__user_dir__, "config.yml")

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
        meta.__ui_index__ = "http://localhost:" + str(port)
    else:
        meta.__ui_index__ = "https://phoenix-slipstream.netlify.app"
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


def cli():
    d = Dvd()
    d.open(g.ARGS.device)
    d.create_backup()


if __name__ == "__main__":
    main()
