import json

class JsonConfig:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.file_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: The file {self.file_path} was not found.") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error: The file {self.file_path} has an incorrect JSON format.") from e

    def field(self, value):
        if value not in self.config:
            raise KeyError(f"Error: The field '{value}' is not present in the configuration.")
        return self.config[value]