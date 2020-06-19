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
import json


class Bridge(object):

    def __init__(self, browser):
        self.browser = browser
        self.execute_js(
            "window.jsScope=angular.element(document.body).scope().common;"
            "window.settings=angular.element(document.getElementById('settings')).scope().settings;"
        )

    def execute_js(self, js, scope=False):
        self.browser.ExecuteJavascript(f"window.jsScope.$apply(function() {{ {js} }});" if scope else js)

    def set_variable(self, js_object, value):
        """set a value to a generic variable using a simple equals operation"""
        self.execute_js(f"{js_object}={self.sanitize_object(value)}")

    def update_dict(self, js_object, dictionary):
        """update key values of a dictionary using Object.assign"""
        self.execute_js(f"Object.assign({js_object}, {self.sanitize_object(dictionary)})")

    def push_to_list(self, js_list, o):
        """push object to a list using .push"""
        self.execute_js(f"{js_list}.push({self.sanitize_object(o)});")

    def popup(self, title, description="", error=False):
        self.execute_js(f"window.jsScope.openToast('{self.sanitize_js(description)}','{self.sanitize_js(title)}', "
                        f"{str(error).lower()});")

    def message(self, title, description=""):
        self.execute_js(f"window.jsScope.openAlert('{self.sanitize_js(title)}', '{self.sanitize_js(description)}');")

    def hide_blocks(self, namespace, blocks):
        self.block_button_handler(namespace, "none", blocks)

    def show_blocks(self, namespace, blocks):
        self.block_button_handler(namespace, "", blocks)

    def block_button_handler(self, namespace, action, item):
        return f"document.getElementById('{namespace}_{item}_{item['type']}').style.display='{action}';"

    def sanitize_object(self, o):
        if isinstance(o, str):
            return f"'{self.sanitize_js(o)}'"
        if isinstance(o, bool):
            return str(o).lower()
        if isinstance(o, dict) or isinstance(o, list):
            return json.dumps(o)
        return o

    @staticmethod
    def sanitize_js(s):
        return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
