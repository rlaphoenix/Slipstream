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
SYSTEM_INFO = ",".join(map(str, filter(None, [
    sys.platform,
    f"{8 * struct.calcsize('P')}bit",
    platform.python_version(),
    [None, "frozen"][IS_FROZEN]
])))


class Config:
    def __init__(self, config_path: Path, **kwargs: Any):
        self.config_path = config_path

        self.last_opened_directory: Optional[Path] = kwargs.get("last_opened_directory") or None
        self.recently_opened: List[Device] = kwargs.get("recently_opened") or []

    @classmethod
    def load(cls, path: Path) -> Config:
        if not path.exists():
            raise FileNotFoundError(f"Config file path ({path}) was not found")
        if not path.is_file():
            raise FileNotFoundError(f"Config file path ({path}) is not to a file.")
        instance: Config = jsonpickle.loads(path.read_text(encoding="utf8"))
        instance.config_path = path
        return instance

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


config = Config.load(Directories.user_data / "config.json")
