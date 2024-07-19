import initialize_modules
from models import get_model
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
        
        Raises:
            ValueError: If the current model is not recognized
        """
        
        model_name = self.config.get_current_model()
        
        model = get_model(model_name)
        if model is None:
            raise ValueError(f"Unknown model: {model_name}")
        
        return model        
