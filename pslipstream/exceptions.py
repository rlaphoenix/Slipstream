class TkinterVersionError(Exception):
    """Tkinter version is too outdated, update tkinter to continue."""


class WindowHandleError(Exception):
    """Couldn't obtain the GUI's window handle."""


class SlipstreamUiError(Exception):
    """Failed to load the UI."""


class SlipstreamDiscInUse(Exception):
    """A disc is already initialised in this instance."""


class SlipstreamNoKeysObtained(Exception):
    """No keys were returned, unable to decrypt."""


class SlipstreamReadError(Exception):
    """An unexpected read error occurred."""


class SlipstreamSeekError(Exception):
    """An unexpected seek error occurred."""
