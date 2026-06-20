import sys
import tomllib
from pathlib import Path

# Single source of truth for the version is [project].version in pyproject.toml; read it here so
# there is only one place to bump. tomllib is part of the standard library (Python 3.11+), so this
# needs no third-party dependency. The frozen build bundles pyproject.toml at the bundle root, see
# pyinstaller.py.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _project_root = Path(getattr(sys, "_MEIPASS"))
else:
    _project_root = Path(__file__).resolve().parent.parent

with (_project_root / "pyproject.toml").open("rb") as _f:
    __version__: str = tomllib.load(_f)["project"]["version"]
