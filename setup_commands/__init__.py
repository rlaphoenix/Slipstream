import os
import sys
from shutil import rmtree

import pslipstream.cfg as cfg


def print_bold(s):
    """Prints things in bold."""
    print("\033[1m{0}\033[0m".format(s))


def build_clean():
    print_bold("Removing previous builds…")
    try:
        rmtree(os.path.join(cfg.root_dir, "dist"))
    except OSError:
        pass
    try:
        rmtree(os.path.join(cfg.root_dir, "build"))
    except OSError:
        pass


def build():
    build_clean()
    print_bold("Ensuring an up-to-date environment…")
    os.system("{0} -m pip install --user --upgrade setuptools wheel".format(sys.executable))
    print_bold("Building Source and Wheel (universal) distribution…")
    os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))
