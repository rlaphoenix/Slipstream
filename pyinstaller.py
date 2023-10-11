import itertools
import shutil
import struct
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import List

import click
from PyInstaller.__main__ import run

from pslipstream import __version__


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug mode (keeps leftover build files)")
@click.option("--name", default="Slipstream", help="Set the Project Name")
@click.option("--author", default="rlaphoenix", help="Set the Project Author")
@click.option("--version", default=__version__, help="Set the EXE Version")
@click.option("--icon-file", default="pslipstream/static/img/icon.ico",
              help="Set the Icon file path (must be a .ICO file)")
@click.option("--one-file", is_flag=True, help="Build to a singular .exe file")
@click.option("--console", is_flag=True, help="Show the Console window")
def main(debug: bool, name: str, author: str, version: str, icon_file: str, one_file: bool, console: bool) -> None:
    # Configuration options
    additional_data: List[List[str]] = [
        # local file path, destination in build output
        ["pslipstream/static", "pslipstream/static"],
        [f"submodules/libdvdcss/1.4.3/{8 * struct.calcsize('P')}-bit/libdvdcss-2.dll", "."]
    ]
    hidden_imports: List[str] = []
    extra_args: List[str] = ["-y"]

    # Prepare environment
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    Path("Slipstream.spec").unlink(missing_ok=True)
    version_file = Path("pyinstaller.version.txt")

    # Create Version file
    version_file.write_text(
        dedent(f"""
        VSVersionInfo(
          ffi=FixedFileInfo(
            filevers=({", ".join(version.split("."))}, 0),
            prodvers=({", ".join(version.split("."))}, 0),
            OS=0x40004,  # Windows NT
            fileType=0x1,  # Application
            subtype=0x0  # type is undefined
          ),
          kids=[
            StringFileInfo(
              [
              StringTable(
                '040904b0',
                [StringStruct('CompanyName', '{author}'),
                StringStruct('FileDescription', 'The most informative Home-media backup solution'),
                StringStruct('FileVersion', '{version}'),
                StringStruct('InternalName', '{name}'),
                StringStruct('LegalCopyright', '{f"Copyright (C) 2020-{datetime.now().year} {author}"}'),
                StringStruct('OriginalFilename', 'Slipstream.exe'),
                StringStruct('ProductName', '{name}'),
                StringStruct('ProductVersion', '{version}'),
                StringStruct('Comments', '{name}')])
              ]),
            VarFileInfo([VarStruct('Translation', [1033, 1200])])
          ]
        )
        """).strip(),
        encoding="utf8"
    )

    try:
        run([
            "pslipstream/__main__.py",
            "-n", name,
            "-i", ["NONE", icon_file][bool(icon_file)],
            ["-D", "-F"][one_file],
            ["-w", "-c"][console],
            *itertools.chain(*[["--add-data", ":".join(x)] for x in additional_data]),
            *itertools.chain(*[["--hidden-import", x] for x in hidden_imports]),
            "--version-file", str(version_file),
            *extra_args
        ])
    finally:
        if not debug:
            shutil.rmtree("build", ignore_errors=True)
            Path("Slipstream.spec").unlink(missing_ok=True)
            version_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
