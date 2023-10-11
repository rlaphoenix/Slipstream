import logging
import os
import sys
from datetime import datetime

import click
import coloredlogs

from pslipstream import __version__, gui
from pslipstream.config import SYSTEM_INFO


@click.command()
@click.option("-v", "--version", is_flag=True, default=False, help="Print version information")
@click.option("-d", "--debug", is_flag=True, default=False, help="Enable DEBUG level logs")
@click.option("-l", "--license", "licence", is_flag=True, default=False, help="View license details")
def main(version: bool, debug: bool, licence: bool) -> None:
    """Slipstream—A Home-media Backup Solution"""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    log = logging.getLogger(__name__)
    coloredlogs.install(
        level=log.level,
        logger=log,
        fmt="{asctime} [{levelname[0]}] {name} : {message}",
        style="{"
    )

    if version:
        print(__version__)
        return

    if licence:
        if not os.path.exists("LICENSE"):
            print(
                "License file was not found locally, please ensure this is a licensed distribution.\n"
                "The license can be found at gnu.org: https://www.gnu.org/licenses/gpl-3.0.txt"
            )
            sys.exit(1)
        else:
            with open("LICENSE", mode="rt", encoding="utf-8") as f:
                print(f.read())
            return

    log.info("Slipstream version %s [%s]", __version__, SYSTEM_INFO)
    log.info("Copyright (c) 2020-%d rlaphoenix", datetime.now().year)
    log.info("https://github.com/rlaphoenix/slipstream")

    gui.start()


if __name__ == "__main__":
    main()
