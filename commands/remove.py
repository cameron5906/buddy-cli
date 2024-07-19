import sys
import initialize_modules
from abilities import ABILITIES, get_ability
from models import MODELS
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def remove_ability(ability_name):
    """
    Removes an ability and its corresponding configuration from Buddy.
    
    Args:
        ability_name (str): The name of the ability to remove
    """
    
    config_manager = ConfigManager()
    secure_store = SecureStore()
    found_model = MODELS.get(ability_name)

    if found_model:
        secure_store.remove_api_key(ability_name)
        config_manager.remove_ability(ability_name)
        print_fancy(f"Removed {found_model['name']} model configuration", color="green")
        sys.exit(0)

    if ability_name not in ABILITIES:
        print_fancy(f"Unknown ability '{ability_name}'", color="red")
        sys.exit(1)

    ability = get_ability(ability_name)
    
    if ability is None:
        print_fancy(f"Ability '{ability_name}' is not implemented", color="red")
        sys.exit(1)

    ability.disable()
    config_manager.remove_ability(ability_name)
