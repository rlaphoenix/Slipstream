import os
import subprocess
import sys

from PyInstaller.utils.hooks import get_package_paths
from setuptools import Command

import pslipstream.__version__ as meta
from setup_commands import build_clean, print_bold


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
        build_clean()
        print_bold("Ensuring supported environment…")
        if not meta.__windows__ and not meta.__linux__ and not meta.__darwin__:
            print("Sorry! Only Windows, Linux and Darwin platforms are supported.")
            sys.exit(1)
        print_bold("Ensuring PyInstaller is available…")
        os.system(
            "{0} -m pip install --user --upgrade pyinstaller".format(sys.executable)
        )
        print_bold("Packing with PyInstaller…")
        sep = ";" if meta.__windows__ else ":"
        sub = subprocess.Popen(
            [
                "pyinstaller",
                "--clean",
                "-F",
                f"{meta.__title_pkg__}/__init__.py",
                "--add-data",
                f"{meta.__title_pkg__}/static{sep}static",
                "--add-data",
                get_package_paths("cefpython3")[1].replace("\\", "/")
                + f"{sep}.",
                "--hidden-import",
                "pkg_resources.py2_warn",
                "-n",
                "Slipstream",
            ]
        )
        sub.communicate()
        if sub.returncode != 0:
            print("Oh no! PyInstaller failed, code=%s" % sub.returncode)
            build_clean()
            sys.exit(1)
        sys.exit()
