import json


class Config:

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = dict()
        self.save_needed = False

        self.reload()

    def __getitem__(self, key):
        return self.config_data[key]

    def __setitem__(self, key, value):
        self.config_data[key] = value

    def __contains__(self, item):
        return item in self.config_data

    def __delitem__(self, key):
        del self.config_data[key]

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=1)

    def reload(self):
        with open(self.config_path, 'r') as f:
            self.config_data = json.load(f)

