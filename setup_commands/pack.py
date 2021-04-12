import os
import subprocess
import sys

from setuptools import Command

import pslipstream.cfg as cfg
from setup_commands import print_bold, clean


class PackCommand(Command):
    """Support setup.py pack."""

    description = "Pack the repo with PyInstaller."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        clean()
        print_bold("Ensuring supported environment…")
        print_bold("Ensuring PyInstaller is available…")
        os.system(
            "{0} -m pip install --user --upgrade pyinstaller".format(sys.executable)
        )
        print_bold("Packing with PyInstaller…")
        sep = ";" if cfg.windows else ":"
        sub = subprocess.Popen(
            [
                "pyinstaller",
                "--clean",
                "-F",
                f"{cfg.title_pkg}/__init__.py",
                "--add-data",
                f"{cfg.title_pkg}/static{sep}static",
                "--hidden-import",
                "pkg_resources.py2_warn",
                "-n",
                "Slipstream",
            ]
        )
        sub.communicate()
        if sub.returncode != 0:
            print("Oh no! PyInstaller failed, code=%s" % sub.returncode)
            clean()
            sys.exit(1)
        sys.exit()
