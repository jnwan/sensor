import yaml


class ConfigSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        try:
            with open("config.yaml", "r") as file:
                self.config_data = yaml.safe_load(file)
        except FileNotFoundError:
            self.config_data = {}
        except Exception as e:
            raise Exception(f"Error loading config: {e}")

    def get_config(self):
        return self.config_data
