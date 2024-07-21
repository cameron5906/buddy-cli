import initialize_models
import sys
from models import create_model, find_models
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

    def get_model(self, require_vision=None, lowest_cost=None):
        """
        Retrieves the name of the current model from the configuration and returns an instance of that model.
        
        Args:
            require_vision (bool): Whether the model must have vision capabilities
            lowest_cost (bool): Whether to return the lowest cost model
        
        Raises:
            ValueError: If the current model is not recognized
        """
                
        provider_name = self.config.get_current_model_provider()
        
        if provider_name is None:
            print_fancy("A model provider has not been configured. Type 'buddy info providers' for more information.", bold=True, color="red")
            sys.exit(1)
        
        applicable_models = find_models(provider_name, vision_capability=require_vision, lowest_cost=lowest_cost)
        
        if len(applicable_models) == 0:
            print_fancy("No models found that match the required criteria. You might want to switch providers.", bold=True, color="red")
            sys.exit(1)

        # Pick the first one
        model = create_model(applicable_models[0])        
        
        return model        
