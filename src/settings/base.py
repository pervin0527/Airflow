import yaml

class BaseConfig:
    def __init__(self, yaml_file_path="src/config/base.yaml"):
        self.config = {}
        self.load_config(yaml_file_path)

    def load_config(self, yaml_file_path):
        try:
            with open(yaml_file_path, 'r') as stream:
                self.config.update(yaml.safe_load(stream))
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {yaml_file_path}")
        except yaml.YAMLError as exc:
            raise RuntimeError(f"Error parsing YAML file: {yaml_file_path}")

    def get(self, key, default=None):
        return self.config.get(key, default)




