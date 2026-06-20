import logging
from datetime import datetime

import coloredlogs

from pslipstream import __version__, gui
from pslipstream.config import SYSTEM_INFO


def main() -> None:
    """Slipstream—A Home-media Backup Solution"""
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    coloredlogs.install(level=log.level, logger=log, fmt="{asctime} [{levelname[0]}] {name} : {message}", style="{")

    log.info("Slipstream version %s [%s]", __version__, SYSTEM_INFO)
    log.info("Copyright (c) 2020-%d rlaphoenix", datetime.now().year)
    log.info("https://github.com/rlaphoenix/slipstream")

    gui.start()


if __name__ == "__main__":
    main()
