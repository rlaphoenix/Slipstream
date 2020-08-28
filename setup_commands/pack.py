import os
import subprocess
import sys

from setuptools import Command

import pslipstream.cfg as cfg
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
        from PyInstaller.utils.hooks import get_package_paths
        build_clean()
        print_bold("Ensuring supported environment…")
        if not cfg.windows and not cfg.linux and not cfg.darwin:
            print("Sorry! Only Windows, Linux and Darwin platforms are supported.")
            sys.exit(1)
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
