from shutil import rmtree

import pslipstream.cfg as cfg


def print_bold(s):
    """Prints things in bold."""
    print("\033[1m{0}\033[0m".format(s))


def clean():
    """Clean build data directories."""
    rmtree(cfg.root_dir / "dist", ignore_errors=True)
    rmtree(cfg.root_dir / "build", ignore_errors=True)
