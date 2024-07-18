import os
import json

CONFIG_FILE = os.path.expanduser('~/.buddy_cli/config.json')


class ConfigManager:
    """
    Manages the configuration of the Buddy CLI.
    """
    
    def __init__(self):
        """
        Initializes the ConfigManager by loading the configuration file.
        """
        
        self.config = {}
        self.load_config()

    def load_config(self):
        """
        Loads the configuration file. If the file does not exist, initializes it with default values.
        """
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"current_model": "gpt4o", "features": []}
            self.save_config()

    def save_config(self):
        """
        Saves the current configuration to disk.
        """
        
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def set_current_model(self, model_name):
        """
        Sets the current model to use for Buddy commands and saves the configuration.
        
        Args:
            model_name (str): The name of the model to use
        """
        
        self.config["current_model"] = model_name
        self.save_config()

    def add_feature(self, feature):
        """
        Enables a feature for Buddy to use and saves the configuration.
        """
        
        if feature not in self.config["features"]:
            self.config["features"].append(feature)
            self.save_config()

    def get_current_model(self):
        """
        Retrieves the current model being used by Buddy.
        """
        
        return self.config.get("current_model", "gpt4o")

    def get_features(self):
        """
        Retrieves the list of features enabled for Buddy.
        """
        
        return self.config.get("features", [])
