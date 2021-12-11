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
import logging
import os
import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication

from pslipstream import logger
from pslipstream.config import config, Directories, System, Project
from pslipstream.ui.main import Main


def main():
    arguments = get_arguments()

    log = logger.setup(level=logging.DEBUG if arguments.dbg else logging.INFO, stream_handler=True)

    for line in get_runtime_details().splitlines(keepends=False):
        if not line:
            continue
        log.info(line)

    if arguments.license:
        if not os.path.exists("LICENSE"):
            print(
                "License file was not found locally, please ensure this is a licensed distribution.\n"
                "The license can be found at gnu.org: https://www.gnu.org/licenses/gpl-3.0.txt"
            )
        else:
            with open("LICENSE", mode="rt", encoding="utf-8") as f:
                print(f.read())
        exit(0)

    gui()


def gui() -> None:
    """Create, Configure, and Show the GUI window."""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setStyleSheet((Directories.static / "style.qss").read_text("utf8"))
    app.aboutToQuit.connect(config.save)

    window = Main()
    window.show()

    sys.exit(app.exec_())


def get_arguments():
    ap = argparse.ArgumentParser()
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
    return ap.parse_args()


def get_runtime_details() -> str:
    return "\n".join([
        Project.license,
        f"{Project.name} v{Project.version} [{System.Info}]",
        Project.description,
        Project.url,
        f"User-Data Directory: {Directories.user_data}",
        f"Static Directory: {Directories.static}",
    ])


if __name__ == "__main__":
    main()
