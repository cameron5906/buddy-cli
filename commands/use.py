import initialize_abilities
import initialize_models
import sys
from abilities import ABILITIES, get_ability
from models import PROVIDER_NAMES
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def use(args):
    """
    Entry point for the 'use' command. Configures Buddy to use a specific model provider or ability.
    
    Args:
        args (list): List of arguments passed to the command
    """
    
    resource_type = args[0]
    
    if resource_type == "provider":
        if len(args) == 3:
            use_model_provider(args[1], args[2])
            sys.exit(0)
        elif len(args) == 2:
            use_model_provider(args[1])
            sys.exit(0)
            
        print_fancy("Usage: buddy use provider <name> <api key>", color="red")
        sys.exit(1)
    elif resource_type == "ability":
        if len(args) > 2:
            use_ability(args[1], args[2:])
            sys.exit(0)
        elif len(args) == 2:
            use_ability(args[1])
            sys.exit(0)
            
        print_fancy("Usage: buddy use ability <name> [options]", color="red")
        sys.exit(1)
    else:
        print("Usage: buddy use <model/ability> [options]")
        sys.exit(1)

    
def use_model_provider(provider_name, api_key=None):
    """
    Configures and enables a model provider for use with Buddy.
    
    Args:
        model_name (str): The name of the model provider to use
        api_key (str): The API key to use with the model
    """
    
    config_manager = ConfigManager()
    secure_store = SecureStore()
    
    if not provider_name in PROVIDER_NAMES:
        print_fancy(f"Model provider {provider_name} not found", bold=True, color="red")
        sys.exit(1)
    
    # If no API key was provided, check if one is already stored. If so, use it.
    if api_key is None and secure_store.get_api_key(provider_name) is not None:
        config_manager.set_current_model_provider(provider_name)
        print_fancy(f"Switched back to {provider_name} models", color="green")
        sys.exit(0)
        
    # If no API key was provided and there's no stored key, fail
    if api_key is None:
        print_fancy(f"API key required for {provider_name}. Use 'buddy use provider {provider_name} <api_key>'", bold=True, color="red")
        sys.exit(1)
    
    secure_store.set_api_key(provider_name, api_key)
    config_manager.set_current_model_provider(provider_name)
    print_fancy(f"Using {provider_name} models", color="green")


def use_ability(ability_name, args=None):
    """
    Enables an ability for Buddy to use.
    
    Args:
        ability_name (str): The name of the ability to enable
        args (list): List of arguments to pass to the ability for configuration
    """
    
    if args is None:
        args = []
    
    if ability_name not in ABILITIES:
        print_fancy(f"Unknown ability '{ability_name}'", color="red")
        sys.exit(1)
    
    config_manager = ConfigManager()

    # Initialize the ability and run the enablement process
    inst = get_ability(ability_name)
    
    enable_result = inst.enable(args)
    
    if enable_result is False:
        print_fancy(f"Failed to enable ability '{ability_name}'", color="red")
        sys.exit(1)
    
    config_manager.add_ability(ability_name)
    
    print_fancy(f"{ability_name} has been enabled", color="green")
