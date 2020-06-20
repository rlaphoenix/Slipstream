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

import ctypes
import platform
import tkinter as tk

from cefpython3 import cefpython as cef

import pslipstream.exceptions as exceptions
from pslipstream.gui.keyboard_handler import KeyboardHandler
from pslipstream.gui.load_handler import LoadHandler


class BrowserFrame(tk.Frame):

    def __init__(self, master, url, js_bindings, on_load=None, on_hot_key=None):
        self.js_bindings = js_bindings
        self.platform = platform.system()
        self.url = url
        self.on_load = on_load
        self.on_hot_key = on_hot_key
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        window_info.SetAsChild(self.get_window_handle(), [0, 0, self.winfo_width(), self.winfo_height()])
        self.browser = cef.CreateBrowserSync(url=self.url, window_info=window_info)
        if self.platform == "Windows":
            window_handle = self.browser.GetOuterWindowHandle()
            insert_after_handle = 0
            SWP_NO_MOVE = 0x0002  # ignore x, y params (don't move to 0, 0)
            ctypes.windll.user32.SetWindowPos(window_handle, insert_after_handle, 0, 0, 1300, 440, SWP_NO_MOVE)
        # Set Handlers
        if self.js_bindings:
            js_bindings_ = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
            if "properties" in self.js_bindings:
                for property_ in self.js_bindings["properties"]:
                    js_bindings_.SetProperty(property_["name"], property_["item"])
            if "objects" in self.js_bindings:
                for object_ in self.js_bindings["objects"]:
                    js_bindings_.SetObject(object_["name"], object_["item"])
            if "functions" in self.js_bindings:
                for function_ in self.js_bindings["functions"]:
                    js_bindings_.SetFunction(function_["name"], function_["item"])
            self.browser.SetJavascriptBindings(js_bindings_)
        self.browser.SetClientHandler(KeyboardHandler())
        self.browser.SetClientHandler(LoadHandler())
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        elif self.platform == "Darwin":
            # On Mac window id is an invalid negative value (Issue #308).
            # This is kind of a dirty hack to get window handle using
            # PyObjC package. If you change structure of windows then you
            # need to do modifications here as well.
            # noinspection PyUnresolvedReferences
            from AppKit import NSApp
            # noinspection PyUnresolvedReferences
            import objc
            # Sometimes there is more than one window, when application
            # didn't close cleanly last time Python displays an NSAlert
            # window asking whether to Reopen that window.
            # noinspection PyUnresolvedReferences
            return objc.pyobjc_id(NSApp.windows()[-1].contentView())
        else:
            raise exceptions.WindowHandleError()

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if self.platform == "Windows":
                ctypes.windll.user32.SetWindowPos(self.browser.GetWindowHandle(), 0, 0, 0, width, height, 0x0002)
            elif self.platform == "Linux":
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None
