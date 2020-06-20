import os
import sys

from setuptools import Command

from setup_commands import print_bold, build


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        build()

        print_bold("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        sys.exit()
