import json


class Config:

    def __init__(self, config_path : str):
        with open(config_path, 'r') as f:
            self.config_data = json.load(f)

    def __getitem__(self, key):
        return self.config_data[key]

