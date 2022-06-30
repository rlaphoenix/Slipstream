#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slipstream - The most informative Home-media backup solution.
Copyright (C) 2020-2021 rlaphoenix

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

Configuration object used to manage the loading and saving of
configuration entries. It deals with everything including the reading and
writing of yaml files, ensuring paths exist, ensuring it has read and write
permissions and such.
"""
import platform
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, List

import yaml
from appdirs import AppDirs


class Config:
    def __init__(self, config_path: Path):
        """Read and Write to/from a User Configuration File."""
        self.config_path = config_path
        self._data = None

    def reload(self):
        """Reload the config by invalidating currently loaded data."""
        self._data = None

    def save(self):
        """Save yaml config to file from dictionary"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, "wt", encoding="utf8") as f:
            yaml.dump(self._data, f)

    @property
    def data(self) -> dict:
        """Load yaml config file as a dictionary."""
        if self._data is not None:
            # only load config data once
            return self._data

        if self.config_path.is_file():
            with open(self.config_path, "rt", encoding="utf8") as f:
                self._data = yaml.load(f, Loader=yaml.Loader)

        return self._data or {}

    @property
    def last_opened_directory(self) -> Optional[str]:
        return self.data.get("last_opened_directory")

    @last_opened_directory.setter
    def last_opened_directory(self, v: Union[Path, str]):
        self.data["last_opened_directory"] = str(v)
        self.save()

    @property
    def recently_opened(self) -> List:
        print(self.data)
        return self.data.get("recently_opened", [])

    @recently_opened.setter
    def recently_opened(self, v: List):
        self.data["recently_opened"] = v
        self.save()


class Directories:
    _app_dirs = AppDirs("pslipstream", "rlaphoenix")
    user_data = Path(_app_dirs.user_data_dir)
    user_log = Path(_app_dirs.user_log_dir)
    user_config = Path(_app_dirs.user_config_dir)
    user_cache = Path(_app_dirs.user_cache_dir)
    user_state = Path(_app_dirs.user_state_dir)
    root = Path(__file__).resolve().parent  # root of package/src
    static = root / "static"


class System:
    _ = platform.system()
    Windows = platform.system() == "Windows"
    Linux = platform.system() == "Linux"
    Mac = platform.system() == "Darwin"
    Frozen = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
    Info = ",".join(map(str, filter(None, [
        sys.platform,
        "%dbit" % (8 * struct.calcsize("P")),
        platform.python_version(),
        [None, "frozen"][Frozen]
    ])))


class Project:
    name = "Slipstream"
    package = "pslipstream"
    author = "rlaphoenix"
    description = "The most informative Home-media backup solution."
    url = "https://github.com/rlaphoenix/Slipstream"
    version = "0.4.0"
    copyright = f"Copyright (C) 2020-{datetime.now().year} {author}"
    license = "\n".join([
        f"{name}  {copyright}",
        "This program comes with ABSOLUTELY NO WARRANTY.",
        "This is free software, and you are welcome to redistribute it",
        f"under certain conditions; type '{package} --license' for details."
    ])


config = Config(Directories.user_data / "config.yml")
