import itertools
import os

from PyInstaller.__main__ import run

"""Configuration options that may be changed or referenced often."""
NAME = "Slipstream"
ICON_FILE = "pslipstream/static/img/icon.ico"  # pass None to use default icon
ONE_FILE = False  # Must be False if using setup.iss
CONSOLE = False  # Recommended if using GUI
ADDITIONAL_DATA = [
    # local file path, destination in build output
    ["pslipstream/static", "static"],
    ["submodules/libdvdcss/1.4.2/64-bit/libdvdcss-2.dll", "libdvdcss-x64.dll"],
    ["submodules/libdvdcss/1.4.2/32-bit/libdvdcss-2.dll", "libdvdcss-x86.dll"]
]
HIDDEN_IMPORTS = ["PySide2.QtXml"]
EXTRA_ARGS = [
    "-y", "--win-private-assemblies", "--win-no-prefer-redirects"
]

"""Run PyInstaller with the provided configuration."""
run([
    "pslipstream/__main__.py",
    "-n", NAME,
    "-i", ["NONE", ICON_FILE][bool(ICON_FILE)],
    ["-D", "-F"][ONE_FILE],
    ["-w", "-c"][CONSOLE],
    *itertools.chain(*[["--add-data", os.pathsep.join(x)] for x in ADDITIONAL_DATA]),
    *itertools.chain(*[["--hidden-import", x] for x in HIDDEN_IMPORTS]),
    *EXTRA_ARGS
])
