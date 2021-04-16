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
        try:
            subprocess.run([
                "pyinstaller",
                "--clean", "--windowed",
                "-F", "%s/__main__.py" % cfg.title_pkg,
                "--add-data", os.pathsep.join([str(cfg.static_dir), "%s/static" % cfg.title_pkg]),
                "--hidden-import", "PySide2.QtXml",
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
