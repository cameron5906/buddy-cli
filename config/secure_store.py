import os
import json

API_KEYS_FILE = os.path.expanduser('~/.buddy_cli/api_keys.json')

class SecureStore:
    def __init__(self):
        self.api_keys = {}
        self.load_keys()

    def load_keys(self):
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r') as f:
                self.api_keys = json.load(f)
        else:
            self.api_keys = {}
            self.save_keys()

    def save_keys(self):
        os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(self.api_keys, f, indent=4)

    def set_api_key(self, service, key):
        self.api_keys[service] = key
        self.save_keys()

    def get_api_key(self, service):
        return self.api_keys.get(service)
