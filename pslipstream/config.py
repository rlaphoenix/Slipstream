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

Configuration object used to manage the loading and saving of
configuration entries. It deals with everything including the reading and
writing of yaml files, ensuring paths exist, ensuring it has read and write
permissions and such.
"""

from pathlib import Path
from typing import Union

import yaml


class Config(object):
    def __init__(self, config_path: Union[Path, str], settings: dict = None):
        self.config_path = Path(config_path)
        self.last_opened_directory = None
        self.recently_opened = []

        if settings:
            self.last_opened_directory = settings.get("last_opened_directory")
            self.recently_opened = settings.get("recently_opened", [])

    @classmethod
    def load(cls, config_path: Union[Path, str]):
        """Load yaml config file as a dictionary"""
        config_path = Path(config_path)
        if not config_path.is_file():
            return cls(config_path)
        with open(config_path, "rt") as f:
            stored_settings = yaml.safe_load(f)
            if not stored_settings:
                return
            return cls(config_path, stored_settings)

    def save(self):
        """Save yaml config to file from dictionary"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, "wt") as f:
            yaml.dump(self.__dict__ or {}, f)
