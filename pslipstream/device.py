class Device:
    def __init__(self, target: str, make: str = None, model: str = None, revision: str = None, volume_id: str = None):
        self.target = target
        self.make = make
        self.model = model
        self.revision = revision
        self.volume_id = volume_id
