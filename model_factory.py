import initialize_models
import sys
from models import get_model
from config.config_manager import ConfigManager
from utils.shell_utils import print_fancy


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
                
        model_name = self.config.get_current_model_provider()
        
        model = get_model(model_name)
        if model is None:
            print_fancy("A model has not been configured. Type 'buddy info' for more information.", bold=True, color="red")
            sys.exit(1)
        
        return model        
