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
        print_bold("Packing with PyInstaller…")
        sep = ";" if cfg.windows else ":"
        try:
            subprocess.run([
                "pyinstaller",
                "--clean",
                "-F", f"{cfg.title_pkg}/__main__.py",
                "--add-data", sep.join([
                    f"{cfg.title_pkg}/static",
                    "static"
                ]),
                "--hidden-import", "pkg_resources.py2_warn",  # TODO: Still needed?
                "-n", "Slipstream"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print("Oh no! PyInstaller failed, code=%s" % e.returncode)
            print("Error log:")
            print(e.stderr)
            sys.exit(1)
        finally:
            clean()
        sys.exit()
