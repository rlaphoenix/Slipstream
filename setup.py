#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Greets to https://github.com/navdeep-G/setup.py

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

from setuptools import find_packages, setup

import pslipstream.cfg as cfg
from setup_commands.pack import PackCommand

try:
    long_description = ("\n" + (cfg.root_dir / "README.md").read_text("utf8"), "text/markdown")
except FileNotFoundError:
    long_description = (cfg.description, "text/plain")

setup(
    name=cfg.title_pkg,
    version=cfg.version,
    description=cfg.description,
    long_description=long_description[0],
    long_description_content_type=long_description[1],
    author=cfg.author,
    author_email=cfg.author_email,
    python_requires=cfg.py_ver_support,
    url=cfg.url,
    project_urls={
        # todo ; "Documentation": '...',
        "Source": "https://github.com/rlaPHOENiX/Slipstream",
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [f"{cfg.title_pkg}={cfg.title_pkg}.slipstream:main"]
    },
    install_requires=cfg.req_packages,
    extras_require=cfg.opt_packages,
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md", "HISTORY.md", "static/*"]
    },
    license=cfg.licence,
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
    cmdclass={"pack": PackCommand},
)
