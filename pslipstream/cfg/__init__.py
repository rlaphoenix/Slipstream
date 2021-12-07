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

# environment
py_version = platform.python_version()
architecture = platform.architecture()[0]
platform = platform.system()
frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
windows = platform == "Windows"
linux = platform == "Linux"
darwin = platform == "Darwin"

# licensing and copyright
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

# objects
user_cfg = None  # gotten on main()
