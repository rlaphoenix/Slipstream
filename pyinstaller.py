import itertools
import os
import shutil
import struct
from pathlib import Path

from PyInstaller.__main__ import run
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct, \
    VarFileInfo, VarStruct, SetVersion

"""Configuration options that may be changed or referenced often."""
DEBUG = False  # When False, removes un-needed data after build has finished
NAME = "Slipstream"
AUTHOR = "PHOENiX"
VERSION = "0.4.0"
ICON_FILE = "pslipstream/static/img/icon.ico"  # pass None to use default icon
ONE_FILE = False  # Must be False if using setup.iss
CONSOLE = False  # Recommended if using GUI
ADDITIONAL_DATA = [
    # local file path, destination in build output
    ["pslipstream/static", "static"],
    ["submodules/libdvdcss/1.4.2/%d-bit/libdvdcss-2.dll" % (8 * struct.calcsize("P")), ""]
]
HIDDEN_IMPORTS = ["PySide2.QtXml"]
EXTRA_ARGS = [
    "-y", "--win-private-assemblies", "--win-no-prefer-redirects"
]

"""Prepare environment to ensure output data is fresh."""
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
Path("Slipstream.spec").unlink(missing_ok=True)

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

"""Set Version Info Structure."""
VERSION_4_TUP = tuple(map(int, ("%s.0" % VERSION).split(".")))
VERSION_4_STR = ".".join(map(str, VERSION_4_TUP))
SetVersion(
    "dist/{0}/{0}.exe".format(NAME),
    VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=VERSION_4_TUP,
            prodvers=VERSION_4_TUP
        ),
        kids=[
            StringFileInfo([StringTable(
                "040904B0",  # ?
                [
                    StringStruct("Comments", NAME),
                    StringStruct("CompanyName", AUTHOR),
                    StringStruct("FileDescription", "The most informative Home-media backup solution"),
                    StringStruct("FileVersion", VERSION_4_STR),
                    StringStruct("InternalName", NAME),
                    StringStruct("LegalCopyright", "Copyright (C) 2021 %s" % AUTHOR),
                    StringStruct("OriginalFilename", ""),
                    StringStruct("ProductName", NAME),
                    StringStruct("ProductVersion", VERSION_4_STR)
                ]
            )]),
            VarFileInfo([VarStruct("Translation", [0, 1200])])  # ?
        ]
    )
)

if not DEBUG:
    shutil.rmtree("build", ignore_errors=True)
    Path("Slipstream.spec").unlink(missing_ok=True)
