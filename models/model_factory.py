from config.config_manager import ConfigManager
from models.gpt4o import GPT4OModel


class ModelFactory:

    def __init__(self):
        self.config = ConfigManager()

    def get_model(self):
        model_name = self.config.get_current_model()
        
        if model_name == "gpt4o":
            return GPT4OModel()
        else:
            raise ValueError(f"Unknown model: {model_name}")
