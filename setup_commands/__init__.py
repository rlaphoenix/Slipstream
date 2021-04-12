import os
import sys
from shutil import rmtree

import pslipstream.cfg as cfg


def print_bold(s):
    """Prints things in bold."""
    print("\033[1m{0}\033[0m".format(s))


def clean():
    """Clean build data directories."""
    rmtree(cfg.root_dir / "dist", ignore_errors=True)
    rmtree(cfg.root_dir / "build", ignore_errors=True)


def build(clean_prior=True):
    """Build source and universal wheel distributions."""
    if clean_prior:
        print_bold("Removing previous builds…")
        clean()
    print_bold("Ensuring an up-to-date environment…")
    os.system(f"{sys.executable} -m pip install --user --upgrade setuptools wheel")
    print_bold("Building Source and Wheel (universal) distribution…")
    os.system(f"{sys.executable} setup.py sdist bdist_wheel --universal")
