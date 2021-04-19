class Device:
    def __init__(self, target: str, medium: str = None, make: str = None, model: str = None, revision: str = None,
                 volume_id: str = None):
        self.target = target
        self.medium = medium
        self.make = make or "Virtual"
        self.model = model or "FS"
        self.revision = revision
        self.volume_id = volume_id

        self.is_file = target.lower().endswith(".iso") or target.lower().endswith(".ifo")
