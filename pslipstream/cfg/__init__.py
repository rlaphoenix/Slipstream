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

Metadata used throughout the application.
By calculating all the metadata in meta.py, it allows us
to easily expose the information to the user via import as well as
throughout the code by importing only what we want.
"""

import datetime
import os
import platform
import sys
from pathlib import Path

# general
title = "Slipstream"
title_pkg = "pslipstream"
description = "The most informative Home-media backup solution."
url = "https://github.com/rlaPHOENiX/Slipstream"
version = "0.4.0"
author = "PHOENiX"
author_email = "rlaphoenix@pm.me"
min_size = "1200x440"

# build configuration
py_ver_support = ">=3.6, <3.10"
# noinspection SpellCheckingInspection
req_packages = [
    # general
    "appdirs>=1.4.4",
    "tqdm>=4.46.1",
    # windows api
    "pywin32>=228; os_name == 'nt'",
    # parsing, syntax, and validators
    "PyYAML>=5.3.1",
    "python-dateutil>=2.8.1",
    # general disc operations
    "pycdlib>=1.10.0",
    # dvd disc operations
    "pydvdcss>=1.0.7.post0",
    "rlapydvdid>=1.2"  # fork of pydvdid, faster and doesn't need mount permission
]
# noinspection SpellCheckingInspection
opt_packages = {
    # build related
    "packing support": ["PyInstaller"]  # provide no version to let the user decide
}

# environment
py_version = platform.python_version()
architecture = platform.architecture()[0]
platform = platform.system()
frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
windows = platform == "Windows"
linux = platform == "Linux"
darwin = platform == "Darwin"

# licensing and copyright
licence = "GPLv3"
copyright_line = f"Copyright (C) 2020-{datetime.datetime.now().year} {author}"
copyright_paragraph = "\n".join([
    f"{title}  {copyright_line}",
    "This program comes with ABSOLUTELY NO WARRANTY.",
    "This is free software, and you are welcome to redistribute it",
    f"under certain conditions; type '{title_pkg} --license' for details."
])

# directories
root_dir = Path(os.path.abspath(os.path.dirname(__file__))).parent
user_dir = None  # gotten on main()
static_dir = root_dir / "static"

# file paths
config_file = None  # gotten on main()
icon_file = os.path.join(static_dir, "icon.png")
ui_index = None  # prefix with `file://` for local file

# objects
user_cfg = None  # gotten on main()
