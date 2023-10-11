from typing import Optional


class Device:
    def __init__(
        self,
        target: str,
        medium: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        revision: Optional[str] = None,
        volume_id: Optional[str] = None
    ):
        self.target = target
        self.medium = medium
        self.make = make or "Virtual"
        self.model = model or "FS"
        self.revision = revision
        self.volume_id = volume_id

        self.is_file = target.lower().endswith(".iso") or target.lower().endswith(".ifo")
