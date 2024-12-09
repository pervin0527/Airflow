from settings.base import BaseConfig

class DevConfig(BaseConfig):
    def __init__(self):
        super().__init__("src/config/base.yaml")
        self.load_config("src/config/dev.yaml")