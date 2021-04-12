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
import os
import sys

from PySide6.QtWidgets import QApplication
from appdirs import user_data_dir

import pslipstream.cfg as cfg
from pslipstream.config import Config
from pslipstream.log import Log
from pslipstream.progress import Progress
from pslipstream.ui.main import UI


def main():
    cfg.user_dir = user_data_dir(cfg.title_pkg, cfg.author)
    cfg.config_file = os.path.join(cfg.user_dir, "config.yml")

    # Initialize custom global variables
    g.ARGS = get_arguments()
    g.LOG = Log()  # Logger, everything written here gets print()'d and sent to GUI
    g.PROGRESS = Progress()  # Progress Bar, controls only the GUI's progress bar.
    g.DBG = g.ARGS.dbg  # Debug switch, enables debugging specific code and logging
    g.CFG = Config(cfg.config_file)
    g.CFG.load()

    if g.ARGS.license:
        if not os.path.exists("LICENSE"):
            print(
                "License file was not found locally, please ensure this is a licensed distribution.\n"
                "The license can be found at gnu.org: https://www.gnu.org/licenses/gpl-3.0.txt"
            )
        else:
            with open("LICENSE", mode="rt", encoding="utf-8") as f:
                print(f.read())
        exit(0)

    g.LOG.write(get_runtime_details() + "\n")

    if g.ARGS.cli:
        cli()
    else:
        gui()


def gui():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    with open(cfg.root_dir / "ui" / "style.qss", "rt", encoding="utf8") as f:
        app.setStyleSheet(f.read())

    ui = UI()
    ui.show()

    ui.scan_devices()

    ui.widget.log.append(get_runtime_details())

    sys.exit(app.exec_())


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
            f":: {cfg.platform} {cfg.architecture} (Python v{cfg.py_version})",
            f":: User Directory: {cfg.user_dir}",
            f":: Static Directory: {cfg.static_dir}",
        ]
    )


if __name__ == "__main__":
    gui()
