import os
import json

CONFIG_FILE = os.path.expanduser('~/.buddy_cli/config.json')

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"current_model": "gpt4o", "features": []}
            self.save_config()

    def save_config(self):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def set_current_model(self, model_name):
        self.config["current_model"] = model_name
        self.save_config()

    def add_feature(self, feature):
        if feature not in self.config["features"]:
            self.config["features"].append(feature)
            self.save_config()

    def get_current_model(self):
        return self.config.get("current_model", "gpt4o")

    def get_features(self):
        return self.config.get("features", [])
