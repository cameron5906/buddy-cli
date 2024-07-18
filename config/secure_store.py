import os
import json

API_KEYS_FILE = os.path.expanduser('~/.buddy_cli/api_keys.json')


class SecureStore:
    """
    Manages the storage of API keys for secure services.
    TODO: Store keys in a more secure manner ;)
    """
    
    def __init__(self):
        """
        Initializes the SecureStore by loading the API keys file.
        """
        
        self.api_keys = {}
        self.load_keys()

    def load_keys(self):
        """
        Loads the API keys file. If the file does not exist, initializes it with an empty dictionary.
        """
        
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r') as f:
                self.api_keys = json.load(f)
        else:
            self.api_keys = {}
            self.save_keys()

    def save_keys(self):
        """
        Saves the current API keys to disk, overwriting the existing file.
        """
        
        os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(self.api_keys, f, indent=4)

    def set_api_key(self, service, key):
        """
        Sets the API key for a given service and saves the keys to disk.
        """
        
        self.api_keys[service] = key
        self.save_keys()

    def get_api_key(self, service):
        """
        Retrieves the API key for a given service.
        
        Raises:
            ValueError: If no API key is found for the given service.
        """
        
        if service not in self.api_keys:
            raise ValueError(f"No API key found for service: {service}")
        
        return self.api_keys.get(service)
