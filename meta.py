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

import pkg_resources

# general
__title__ = "Slipstream"
__title_pkg__ = "pslipstream"
__description__ = "The most informative Home-media backup solution."
__url__ = "https://github.com/rlaPHOENiX/Slipstream"
__version__ = "0.1.6"
__author__ = "PHOENiX"
__author_email__ = "rlaphoenix@pm.me"
__min_size__ = "1200x440"
__package_obj__ = None
try:
    __package_obj__ = pkg_resources.Requirement.parse(f"{__title_pkg__}=={__version__}")
except pkg_resources.DistributionNotFound:
    pass

# build configuration
__py_ver_support__ = ">=3.6"
# noinspection SpellCheckingInspection
__req_packages__ = [
    # general
    "appdirs>=1.4.4",
    "tqdm>=4.46.1",
    # cef
    "cefpython3==66.0",
    "pyobjc; sys_platform == 'darwin'",
    "AppKit; sys_platform == 'darwin'",
    # http and such
    "requests>=2.24.0",
    # parsing, syntax, and validators
    "PyYAML>=5.3.1",
    "python-dateutil>=2.8.1",
    # general disc operations
    "pycdlib>=1.10.0",
    # dvd disc operations
    "pydvdcss>=1.0.7.post0",
    "pydvdid @ git+https://git@github.com/rlaPHOENiX/pydvdid@master"  # fork
]
# noinspection SpellCheckingInspection
__opt_packages__ = {
    # build related
    "packing support": ["PyInstaller"]  # provide no version to let the user decide
}

# environment
__cef_version__ = None  # gotten on main()
__py_version__ = platform.python_version()
__architecture__ = platform.architecture()[0]
__platform__ = platform.system()
__windows__ = __platform__ == "Windows"
__linux__ = __platform__ == "Linux"
__darwin__ = __platform__ == "Darwin"

# licensing and copyright
__license__ = "GPLv3"
__copyright__ = f"Copyright (C) {datetime.datetime.now().year} {__author__}"
__copyright_paragraph__ = "\n".join([
    f"{__title__}  {__copyright__}",
    "This program comes with ABSOLUTELY NO WARRANTY.",
    "This is free software, and you are welcome to redistribute it",
    f"under certain conditions; type '{__title_pkg__} --license' for details."
])

# directories
__root_dir__ = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
__user_dir__ = None  # gotten on main()
__static_dir__ = os.path.join(__root_dir__, "static")
if __package_obj__:
    try:
        __static_dir__ = pkg_resources.resource_filename(__package_obj__, f"{__title_pkg__}/static")
    except pkg_resources.DistributionNotFound:
        pass
    except pkg_resources.VersionConflict:
        pass

# file paths
__config_file__ = None  # gotten on main()
__icon_file__ = os.path.join(__static_dir__, "icon.png")
__ui_index__ = None  # prefix with `file://` for local file
