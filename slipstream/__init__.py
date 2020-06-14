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

# slipstream
import slipstream.__version__ as meta
from slipstream.config import Config
from slipstream.gui import Gui


def main():

    # Print Copyright
    print(meta.__copyright_paragraph__ + "\n")

    # Parse Arguments
    ArgParser = argparse.ArgumentParser()
    ArgParser.add_argument(
        "--license",
        action="store_true",
        default=False,
        required=False,
        help="View license details",
    )
    args = ArgParser.parse_args()

    # Show License if asked
    if args.license:
        with open("LICENSE", "rt", "utf-8") as f:
            print(f.read())
        exit(0)
    
    # Initialize custom global variables
    g.DBG = False
    g.CFG = Config(meta.__config_file__)
    g.CFG.load()

    # Print Runtime Details
    print("\n".join([
        f":: {meta.__title__} v{meta.__version__}",
        f"{meta.__description__}",
        f"{meta.__url__}",
        f":: {'DEBUG' if g.DBG else 'Standard'} MODE",
        f":: {meta.__platform__} {meta.__architecture__} (Python v{meta.__py_version__})",
        f":: CEF Runtime: {meta.__cef_version__}",
        f":: User Directory: {meta.__user_dir__}",
        f":: Static Directory: {meta.__static_dir__}"
    ]) + "\n")

    # Start GUI
    Gui(
        url=meta.__ui_index__,
        icon=meta.__icon_file__,
        js_bindings={
            "properties": [
                {
                    "name": "config",
                    "item": g.CFG.settings
                }
            ],
            "functions": [
                {"name": "pyDelete", "item": os.remove},
                {"name": "pyHref", "item": lambda url: webbrowser.open(url)},
                {"name": "configSave", "item": g.CFG.save},
            ],
        },
    ).mainloop()


if __name__ == "__main__":
    main()
