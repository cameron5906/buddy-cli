import sys
import initialize_modules
from abilities import ABILITIES, get_ability
from models import MODELS
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def remove(args):
    """
    Entry point for the 'remove' command. Removes a model or ability from Buddy.
    
    Args:
        args (list): List of arguments passed to the command
    """
    
    resource_type = args[0]
    
    if resource_type == "model":
        if len(args) < 2:
            print_fancy("Usage: buddy remove model <name>", color="red")
            sys.exit(1)
            
        remove_model(args[1])
    elif resource_type == "ability":
        if len(args) < 2:
            print_fancy("Usage: buddy remove ability <name>", color="red")
            sys.exit(1)
            
        remove_ability(args[1])
    else:
        print("Usage: buddy remove <model/ability> <name>")
        sys.exit(1)


def remove_model(model_name):
    """
    Removes configuration for a model from Buddy.
    
    Args:
        model_name (str): The name of the model to remove
    """
    
    current_model_name = ConfigManager().get_current_model()
    
    if model_name == current_model_name:
        print_fancy("Cannot remove the current model. Please switch to another model first using 'buddy use model <name>'.", color="red")
        sys.exit(1)
        
    if model_name not in MODELS:
        print_fancy(f"Unknown model '{model_name}'", color="red")
        sys.exit(1)
        
    secure_store = SecureStore()
    secure_store.remove_api_key(model_name)
    
    print_fancy(f"Removed {MODELS[model_name]['name']} model configuration", color="green")


def remove_ability(ability_name):
    """
    Disables and removes configuration for an ability from Buddy.
    
    Args:
        ability_name (str): The name of the ability to remove
    """
    
    config_manager = ConfigManager()

    if ability_name not in ABILITIES:
        print_fancy(f"Unknown ability '{ability_name}'", color="red")
        sys.exit(1)

    ability = get_ability(ability_name)
    
    ability.disable()
    config_manager.remove_ability(ability_name)
    
    print_fancy(f"Removed {ability.name} ability", color="green")
