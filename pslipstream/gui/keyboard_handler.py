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


class KeyboardHandler:

    # Important: Functions cannot be static!

    def OnKeyEvent(self, browser, event, **_):
        """Called after the renderer and javascript in the page has had a chance to handle the event."""
        if event["type"] == 3:
            # CTRL+SHIFT+I - Open Dev Tools
            if event["modifiers"] == 6 and event["native_key_code"] == 31:
                browser.ShowDevTools()
