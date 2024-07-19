import sys
import initialize_modules
from features import FEATURES, get_feature
from models import MODELS
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def use_feature(args):
    """
    Configures Buddy to use a specific model or feature.
    
    Args:
        args (list): List of arguments passed to the command
    """
    
    config_manager = ConfigManager()
    secure_store = SecureStore()

    if len(args) < 1:
        print("Usage: buddy use <feature> [value]")
        return

    feature = args[0]
    value = args[1] if len(args) > 1 else None

    found_model = MODELS.get(feature)
    if found_model:
        if not value:
            print("Usage: buddy use <model> <api key>")
            return

        secure_store.set_api_key(feature, value)
        config_manager.set_current_model(feature)
        return

    if feature not in FEATURES:
        print_fancy(f"Unknown feature: {feature}", color="red")
        sys.exit(1)
    
    inst = get_feature(feature)
    inst.enable(args[1:])
    config_manager.add_feature(feature)
