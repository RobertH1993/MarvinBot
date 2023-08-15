import json


class Config:

    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config_data = dict()
        self.reload()

    def __getitem__(self, key):
        return self._config_data[key]

    def __setitem__(self, key, value):
        self._config_data[key] = value

    def __contains__(self, item):
        return item in self._config_data

    def __delitem__(self, key):
        del self._config_data[key]

    def save(self):
        with open(self._config_path, 'w') as f:
            json.dump(self._config_data, f, indent=1)

    def reload(self):
        with open(self._config_path, 'r') as f:
            self._config_data = json.load(f)

