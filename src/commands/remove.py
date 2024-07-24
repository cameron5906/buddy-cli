import initialize_models
import initialize_abilities
import sys
from abilities import ABILITIES, get_ability
from models import PROVIDER_NAMES
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def remove(args):
    """
    Entry point for the 'remove' command. Removes a model provider or ability from Buddy.
    
    Args:
        args (list): List of arguments passed to the command
    """
    
    resource_type = args[0]
    
    if resource_type == "provider":
        if len(args) < 2:
            print_fancy("Usage: buddy remove provider <name>", color="red")
            sys.exit(1)
            
        remove_model_provider(args[1])
    elif resource_type == "ability":
        if len(args) < 2:
            print_fancy("Usage: buddy remove ability <name>", color="red")
            sys.exit(1)
            
        remove_ability(args[1])
    else:
        print("Usage: buddy remove <model/ability> <name>")
        sys.exit(1)


def remove_model_provider(provider_name):
    """
    Removes configuration for a model provider from Buddy.
    
    Args:
        model_name (str): The name of the model provider to disable
    """
    
    current_provider_name = ConfigManager().get_current_model_provider()
    
    if provider_name == current_provider_name:
        print_fancy("Cannot remove the current model provider. Please switch to another provider first using 'buddy use provider <name> [api_key]'.", color="red")
        sys.exit(1)
        
    if provider_name not in PROVIDER_NAMES:
        print_fancy(f"Unknown provider '{provider_name}. Use 'buddy info providers' for more information.'", color="red")
        sys.exit(1)
        
    secure_store = SecureStore()
    secure_store.remove_api_key(provider_name)
    
    print_fancy(f"Removed {provider_name} configuration", color="green")


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
