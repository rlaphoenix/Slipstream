import logging
import sys

try:
    import coloredlogs
except ImportError:
    pass

LOG_FORMAT = "{asctime} [{levelname[0]}] {name} : {message}"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = "{"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT, LOG_STYLE)


def setup(name: str = None, level: int = logging.INFO, stream_handler=False) -> logging.Logger:
    """
    Create a log handler for the specified name, and deals with the log and date formatting automatically.
    :param name: Log name. If `None` it will apply to the base/root logger.
    :param level: Default initial log level. This should be a Constant from `logging`, e.g. `logging.INFO`.
    :param stream_handler: Adds a StreamHandler, sending the log to the CLI stream.
    :returns: Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if stream_handler:
        sh = logging.StreamHandler()
        sh.setFormatter(LOG_FORMATTER)
        logger.addHandler(sh)
    if "coloredlogs" in sys.modules:
        coloredlogs.install(level=level, logger=logger, fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, style=LOG_STYLE)
    return logger
