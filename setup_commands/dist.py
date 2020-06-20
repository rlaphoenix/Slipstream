import sys

from setuptools import Command

from setup_commands import build


class DistCommand(Command):
    """Support setup.py build."""

    description = "Build the package."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        build()
        sys.exit()
