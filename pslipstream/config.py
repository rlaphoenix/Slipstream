from __future__ import annotations

import platform
import struct
import sys
from pathlib import Path
from typing import Any, List, Optional

import jsonpickle
from appdirs import AppDirs

from pslipstream.device import Device

IS_FROZEN = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
SYSTEM_INFO = ",".join(
    map(
        str,
        filter(
            None,
            [sys.platform, f"{8 * struct.calcsize('P')}bit", platform.python_version(), [None, "frozen"][IS_FROZEN]],
        ),
    )
)


# User-tunable read settings and their defaults. Kept here so older config files (which predate a
# setting) transparently gain its default on load.
SETTINGS_DEFAULTS: dict[str, Any] = {
    # libdvdcss CSS title-key method (DVDCSS_METHOD): "key" (default), "disc", "title", or "unset".
    "css_crack_mode": "key",
    # libdvdcss verbosity (DVDCSS_VERBOSE): 0 (silent), 1 (errors), 2 (errors + debug, the max).
    "css_verbosity": 2,
    # How many times to retry opening the disc in pycdlib, which can fail while the drive spins up.
    "pycdlib_open_attempts": 5,
    # Seconds to wait between those pycdlib open attempts.
    "pycdlib_open_retry_delay": 1.0,
    # Sectors read at once during a backup (larger = fewer round-trips, more memory).
    "read_buffer_sectors": 128,
    # How many times to retry a raw SCSI read of a sector libdvdcss could not read.
    "scsi_read_attempts": 3,
    # Maximum sectors per raw SCSI read command (drives cap single transfers; 32 = 64 KiB is safe).
    "scsi_max_transfer_sectors": 32,
}


class Config:
    def __init__(self, config_path: Path, **kwargs: Any):
        self.config_path = config_path

        self.last_opened_directory: Optional[Path] = kwargs.get("last_opened_directory") or None
        self.recently_opened: List[Device] = kwargs.get("recently_opened") or []

        # read settings (see SETTINGS_DEFAULTS for descriptions)
        self.css_crack_mode: str = kwargs.get("css_crack_mode", SETTINGS_DEFAULTS["css_crack_mode"])
        self.css_verbosity: int = kwargs.get("css_verbosity", SETTINGS_DEFAULTS["css_verbosity"])
        self.pycdlib_open_attempts: int = kwargs.get(
            "pycdlib_open_attempts", SETTINGS_DEFAULTS["pycdlib_open_attempts"]
        )
        self.pycdlib_open_retry_delay: float = kwargs.get(
            "pycdlib_open_retry_delay", SETTINGS_DEFAULTS["pycdlib_open_retry_delay"]
        )
        self.read_buffer_sectors: int = kwargs.get("read_buffer_sectors", SETTINGS_DEFAULTS["read_buffer_sectors"])
        self.scsi_read_attempts: int = kwargs.get("scsi_read_attempts", SETTINGS_DEFAULTS["scsi_read_attempts"])
        self.scsi_max_transfer_sectors: int = kwargs.get(
            "scsi_max_transfer_sectors", SETTINGS_DEFAULTS["scsi_max_transfer_sectors"]
        )

    @classmethod
    def load(cls, path: Path) -> Config:
        if not path.exists():
            raise FileNotFoundError(f"Config file path ({path}) was not found")
        if not path.is_file():
            raise FileNotFoundError(f"Config file path ({path}) is not to a file.")
        instance: Config = jsonpickle.loads(path.read_text(encoding="utf8"))
        instance.config_path = path
        # backfill any settings added since this config file was written
        for key, default in SETTINGS_DEFAULTS.items():
            if not hasattr(instance, key):
                setattr(instance, key, default)
        return instance

    def reset_settings(self) -> None:
        """Restore all read settings to their defaults (does not touch recent files)."""
        for key, default in SETTINGS_DEFAULTS.items():
            setattr(self, key, default)

    def save(self) -> None:
        config_path_backup = self.config_path

        del self.config_path
        pickled_config = jsonpickle.dumps(self)
        self.config_path = config_path_backup

        config_path_backup.parent.mkdir(parents=True, exist_ok=True)
        config_path_backup.write_text(pickled_config, encoding="utf8")


class Directories:
    _app_dirs = AppDirs("pslipstream", "rlaphoenix")
    user_data = Path(_app_dirs.user_data_dir)
    user_log = Path(_app_dirs.user_log_dir)
    user_config = Path(_app_dirs.user_config_dir)
    user_cache = Path(_app_dirs.user_cache_dir)
    user_state = Path(_app_dirs.user_state_dir)
    root = Path(__file__).resolve().parent  # root of package/src
    static = root / "static"


config_path = Directories.user_data / "config.json"
if not config_path.exists():
    config = Config(config_path)
else:
    config = Config.load(config_path)
