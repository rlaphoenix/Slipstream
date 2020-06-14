#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Greetz to https://github.com/navdeep-G/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

import slipstream.__version__ as meta

# Package meta-data. Most of it is loaded from ./{name}/__version__.py
NAME = meta.__title__.lower()
REQUIRES_PYTHON = ">=3.6.0"

# What packages are required for this module to be executed?
REQUIRED = [
  # general
  "pyyaml>=5.3",
  "appdirs>=1.4.3",
  # cef
  "cefpython3>=66.0",
  "pyobjc; sys_platform == 'darwin'",
  "appkit; sys_platform == 'darwin'",
  # http and such
  "requests>=2.23.0",
  "python-status>=1.0.1",
  # parsing, syntax, and validators
  "validate_email>=1.3"
]

# What packages are optional?
EXTRAS = {
  # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
  with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()
except FileNotFoundError:
  long_description = meta.__description__


class UploadCommand(Command):
  """Support setup.py upload."""

  description = "Build and publish the package."
  user_options = []

  @staticmethod
  def status(s):
    """Prints things in bold."""
    print("\033[1m{0}\033[0m".format(s))

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    try:
      self.status("Removing previous builds…")
      rmtree(os.path.join(here, "dist"))
    except OSError:
      pass

    self.status("Building Source and Wheel (universal) distribution…")
    os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

    self.status("Uploading the package to PyPI via Twine…")
    os.system("twine upload dist/*")

    self.status("Pushing git tags…")
    os.system("git tag v{0}".format(meta.__version__))
    os.system("git push --tags")

    sys.exit()


# Where the magic happens:
setup(
  name=NAME,
  version=meta.__version__,
  description=meta.__description__,
  long_description=long_description,
  long_description_content_type="text/markdown",
  author=meta.__author__,
  author_email=meta.__author_email__,
  python_requires=REQUIRES_PYTHON,
  url=meta.__url__,
  project_urls={
    #"Documentation": '...todo...',
    "Source": 'https://github.com/rlaPHOENiX/Slipstream',
  },
  packages=find_packages(),
  py_modules=[NAME],
  entry_points={"console_scripts": [f'{meta.__cmd__}={NAME}.__init__:main']},
  install_requires=REQUIRED,
  extras_require=EXTRAS,
  include_package_data=True,
  package_data={
    "": ["LICENSE", "HISTORY.md"],
    NAME: ["static/*"]
  },
  license=meta.__license__,
  classifiers=[
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Development Status :: 1 - Planning",
    "Natural Language :: English",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "Topic :: Multimedia",
    "Topic :: Multimedia :: Video",
    "Topic :: Multimedia :: Video :: Conversion",
  ],
  # $ setup.py publish support.
  cmdclass={"upload": UploadCommand}
)
