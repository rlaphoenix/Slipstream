import os
import sys

from setuptools import Command

from setup_commands import print_bold, clean


class DistCommand(Command):
    """Support setup.py build."""

    description = "Build source and universal wheel distributions."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        print_bold("Removing previous builds…")
        clean()
        print_bold("Ensuring an up-to-date environment…")
        os.system(f"{sys.executable} -m pip install --user --upgrade setuptools wheel")
        print_bold("Building Source and Wheel (universal) distribution…")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")
        sys.exit()
