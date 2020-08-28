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

import builtins as g
import webbrowser

from pslipstream.exceptions import SlipstreamUiError


class LoadHandler:

    # Important: Functions cannot be static!

    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        if browser.GetIdentifier() != 1:
            return  # this is a href hook, lets just pass
        if not is_loading:
            # browser dom ready
            # ...
            pass

    def OnLoadStart(self, browser, frame):
        """Called when loading starts."""
        # hook and open in users browser instead of inside App
        if browser.GetIdentifier() != 1:
            browser.StopLoad()
            browser.CloseBrowser()
            webbrowser.open(frame.GetUrl())

    def OnLoadError(self, browser, **_):
        """Called when loading errors."""
        if browser.GetIdentifier() != 1:
            return  # this is a href, lets just pass
        if "gatsby-develop" in g.ARGS.dev:
            # gatsby-develop switch needs this to pass, I believe it's caused by the 404 page check
            # failing, and because it failed, OnLoadError gets called.
            return
        raise SlipstreamUiError()
