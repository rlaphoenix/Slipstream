#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Greets to https://github.com/navdeep-G/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

# std
import io
import os

# pip packages
from setuptools import find_packages, setup

# slipstream
import pslipstream.__version__ as meta
from setup_commands.dist import DistCommand
from setup_commands.pack import PackCommand
from setup_commands.upload import UploadCommand

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(meta.__root_dir__, "README.md"), encoding="utf-8") as f:
        long_description = ("\n" + f.read(), "text/markdown")
except FileNotFoundError:
    long_description = (meta.__description__, "text/plain")

# Where the magic happens:
setup(
    name=meta.__title_pkg__,
    version=meta.__version__,
    description=meta.__description__,
    long_description=long_description[0],
    long_description_content_type=long_description[1],
    author=meta.__author__,
    author_email=meta.__author_email__,
    python_requires=meta.__py_ver_support__,
    url=meta.__url__,
    project_urls={
        # todo ; "Documentation": '...',
        "Source": "https://github.com/rlaPHOENiX/Slipstream",
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [f"{meta.__title_pkg__}={meta.__title_pkg__}.__init__:main"]
    },
    install_requires=meta.__req_packages__,
    dependency_links=meta.__req_links__,
    extras_require=meta.__opt_packages__,
    include_package_data=True,
    package_data={
        "": ["LICENSE", "HISTORY.md", "static/*"],
        # meta.__title_pkg__: ["static/*"]
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
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    # $ setup.py publish support.
    cmdclass={"dist": DistCommand, "pack": PackCommand, "upload": UploadCommand},
)
