#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Greetz to https://github.com/navdeep-G/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
import subprocess
from shutil import rmtree

from setuptools import find_packages, setup, Command

from PyInstaller.utils.hooks import get_package_paths

import pslipstream.__version__ as meta

# Package meta-data. Most of it is loaded from ./{name}/__version__.py
REQUIRES_PYTHON = ">=3.6.0"

# What packages are required for this module to be executed?
REQUIRED = [
  # general
  "appdirs>=1.4.3",
  "tqdm>=4.46.1",
  # cef
  "cefpython3>=66.0",
  "pyobjc; sys_platform == 'darwin'",
  "appkit; sys_platform == 'darwin'",
  # http and such
  "requests>=2.23.0",
  # parsing, syntax, and validators
  "pyyaml>=5.3",
  "python-dateutil>=2.8.1",
  # general disc operations
  "pycdlib>=1.10.0",
  # dvd disc operations
  "pydvdcss>=1.0.7.post0",
  #"git+git://github.com/rlaPHOENiX/pydvdid.git#egg=pydvdid",  # fork + update
  # build related
  "PyInstaller"  # provide no version to let the user decide
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

def status(s):
  """Prints things in bold."""
  print("\033[1m{0}\033[0m".format(s))

def build_clean():
  status("Removing previous builds…")
  try:
    rmtree(os.path.join(here, "dist"))
  except OSError:
    pass
  try:
    rmtree(os.path.join(here, "build"))
  except OSError:
    pass

def build():
  build_clean()
  status("Ensuring an up-to-date environment…")
  os.system("{0} -m pip install --user --upgrade setuptools wheel".format(sys.executable))
  status("Building Source and Wheel (universal) distribution…")
  os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))


class UploadCommand(Command):
  """Support setup.py upload."""

  description = "Build and publish the package."
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    build()

    status("Uploading the package to PyPI via Twine…")
    os.system("twine upload dist/*")

    sys.exit()


class BuildCommand(Command):
  """Support setup.py build."""

  description = "Build the package."
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    build()
    sys.exit()


class PackCommand(Command):
  """Support setup.py pack."""

  description = "Pack the repo with PyInstaller."
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    build_clean()
    status("Ensuring supported environment…")
    if not meta.__windows__ and not meta.__linux__ and not meta.__darwin__:
      print("Sorry! Only Windows, Linux and Darwin platforms are supported.")
      sys.exit(1)
    status("Ensuring PyInstaller is available…")
    os.system("{0} -m pip install --user --upgrade pyinstaller".format(sys.executable))
    status("Packing with PyInstaller…")
    sep = ";" if meta.__windows__ else ":"
    sub = subprocess.Popen([
      "pyinstaller", "--clean", "-F", "slipstream/__init__.py",
      "--add-data", f"slipstream/static{sep}static", "--add-data", get_package_paths("cefpython3")[1].replace("\\", "/") + f"{sep}.",
      "--hidden-import", "pkg_resources.py2_warn", "-n", "Slipstream"
    ])
    sub.communicate()
    rcode = sub.returncode
    if rcode != 0:
      print("Oh no! PyInstaller failed, code=%s" % rcode)
      build_clean()
      sys.exit(1)
    sys.exit()


# Where the magic happens:
setup(
  name=meta.__title_pkg__,
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
  entry_points={"console_scripts": [f'{meta.__title_pkg__}={meta.__title_pkg__}.__init__:main']},
  install_requires=REQUIRED,
  extras_require=EXTRAS,
  include_package_data=True,
  package_data={
    "": ["LICENSE", "HISTORY.md", "static/*"],
    #meta.__title_pkg__: ["static/*"]
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
    "Development Status :: 2 - Pre-Alpha",
    "Natural Language :: English",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "Topic :: Multimedia",
    "Topic :: Multimedia :: Video",
    "Topic :: Multimedia :: Video :: Conversion",
  ],
  # $ setup.py publish support.
  cmdclass={
    "upload": UploadCommand,
    "dist": BuildCommand,
    "pack": PackCommand
  }
)
