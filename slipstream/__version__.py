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
By calculating all the metadata in __version__.py, it allows us
to easily expose the information to the user via import as well as
throughout the code by importing only what we want.

"""

# std
import os
import datetime
import platform
import pkg_resources
# pip packages
from cefpython3 import cefpython as cef
from appdirs import user_data_dir


# general
__title__ = "Slipstream"
__description__ = "The most informative Home-media backup solution."
__url__ = "https://github.com/rlaPHOENiX/Slipstream"
__version__ = "0.0.0"
__author__ = "PHOENiX"
__author_email__ = "rlaphoenix@pm.me"
__min_size__ = (1400, 440)  # width, height. todo ; move this to config file
__package_obj__ = None
try:
  __package_obj__ = pkg_resources.Requirement.parse(f"{__title__}=={__version__}")
except pkg_resources.DistributionNotFound:
  pass

# environment
__cmd__ = "slipstream"
__cef_version__ = cef.GetVersion()
__py_version__ = platform.python_version()
__architecture__ = platform.architecture()[0]
__windows__ = platform.system() == "Windows"
__linux__ = platform.system() == "Linux"
__darwin__ = platform.system() == "Darwin"

# licensing and copyright
__license__ = "GPLv3"
__copyright__ = f"Copyright (C) {datetime.datetime.now().year} {__author__}"
__copyright_paragraph__ = """\
%s  %s
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; type '%s --license' for details.
""" % (__title__, __copyright__, __cmd__)

# directories
__root_dir__ = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
__user_dir__ = user_data_dir(__title__, __author__)
__static_dir__ = os.path.join(__root_dir__, "static")
if __package_obj__:
  try:
    __static_dir__ = pkg_resources.resource_filename(__package_obj__, f"{__title__}/assets")
  except pkg_resources.DistributionNotFound:
    pass

# file paths
__config_file__ = os.path.join(__user_dir__, "config.yml")
__icon_file__ = os.path.join(__static_dir__, "icon.png")
__ui_index__ = "file:///home/owner/github/SNIPR-UI/index.html"