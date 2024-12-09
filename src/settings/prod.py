from settings.base import BaseConfig

class ProdConfig(BaseConfig):
    def __init__(self):
        super().__init__("src/config/base.yaml")
        self.load_config("src/config/prod.yaml")