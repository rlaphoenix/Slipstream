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
import webbrowser
# pip packages
from cefpython3 import cefpython as cef
# slipstream
import pslipstream.exceptions as exceptions
from pslipstream.gui.bridge import Bridge


class LoadHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame
    
    def OnLoadStart(self, browser, frame):
        """Called when loading starts."""
        # hook and open in users browser instead of inside App
        if browser.GetIdentifier() != 1:
            browser.StopLoad()
            browser.CloseBrowser()
            webbrowser.open(frame.GetUrl())

    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        if browser.GetIdentifier() != 1:
            return  # this is a href hook, we don't care
        if not is_loading:
            self.browser_frame.bridge = Bridge(browser)
            # js bindings
            if self.browser_frame.js_bindings:
                js_bindings_ = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
                if "properties" in self.browser_frame.js_bindings:
                    for property_ in self.browser_frame.js_bindings["properties"]:
                        js_bindings_.SetProperty(property_["name"], property_["item"])
                if "objects" in self.browser_frame.js_bindings:
                    for object_ in self.browser_frame.js_bindings["objects"]:
                        js_bindings_.SetObject(object_["name"], object_["item"])
                if "functions" in self.browser_frame.js_bindings:
                    for function_ in self.browser_frame.js_bindings["functions"]:
                        js_bindings_.SetFunction(function_["name"], function_["item"])
                self.browser_frame.bridge.browser.SetJavascriptBindings(js_bindings_)
            # browser dom ready
            # ...

    def OnLoadError(self, browser, frame, error_code, error_text_out, **_):
        if browser.GetIdentifier() != 1:
            return  # this is a href hook, we don't care
        #raise exceptions.SlipstreamUiError()
