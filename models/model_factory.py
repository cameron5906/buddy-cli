from config.config_manager import ConfigManager
from models.gpt4o import GPT4OModel


class ModelFactory:
    """
    A factory to create instances of different models based on the current configuration.
    
    Attributes:
        config (ConfigManager): The configuration manager to retrieve the current model from
    """

    def __init__(self):
        """
        Initializes the ModelFactory by creating a ConfigManager instance.
        """
        
        self.config = ConfigManager()

    def get_model(self):
        """
        Retrieves the name of the current model from the configuration and returns an instance of that model.
        """
        
        model_name = self.config.get_current_model()
        
        if model_name == "gpt4o":
            return GPT4OModel()
        
        else:
            raise ValueError(f"Unknown model: {model_name}")
