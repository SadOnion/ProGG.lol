import os
import json

SETTINGS_FILE = 'settings.cfg'


class Settings:
    def __init__(self):
        self.settings = {}
        if os.path.isfile(SETTINGS_FILE):
            self.read()

    def read(self):
        with open(SETTINGS_FILE, 'r') as f:
            self.settings = json.load(f)

    def save(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def getSetting(self, key):
        if key in self.settings:
            return self.settings[key]

        return ''

    def setSetting(self, key, val):
        self.settings[key] = val
