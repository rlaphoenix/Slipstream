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

import os.path

import yaml


class Config(object):
    def __init__(self, config_path):
        self.settings = {
            "-": "-"  # need at least one config entry, otherwise it infinite loops
            # todo ; implement stuff that needs configuration
        }
        self.config_path = config_path

    def get_handle(self, mode="r"):
        """Open a file handle with the specified mode"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        return open(self.config_path, mode)

    def load(self):
        """Load yaml config file as a dictionary"""
        if (
            not os.path.exists(self.config_path) or
            not os.path.isfile(self.config_path) or
            not os.path.exists(self.config_path)
        ):
            # no config file exists yet, let's create base one
            self.save()
        with self.get_handle() as f:
            stored_settings = yaml.safe_load(f)
            if not stored_settings:
                # invalid yaml or empty file, reset the config file and reload
                self.save()
                self.load()
                return
            self.settings = stored_settings

    def save(self, settings=None):
        """Save yaml config to file from dictionary"""
        if settings:
            self.settings = settings
        if self.settings:
            with self.get_handle("w") as f:
                yaml.dump(self.settings, f)
