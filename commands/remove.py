import sys
import initialize_modules
from features import FEATURES, get_feature
from models import MODELS
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy


def remove_feature(feature_name):
    """
    Removes a feature and its corresponding configuration from Buddy.
    
    Args:
        feature_name (str): The name of the feature to remove
    """
    
    config_manager = ConfigManager()
    secure_store = SecureStore()
    found_model = MODELS.get(feature_name)

    if found_model:
        secure_store.remove_api_key(feature_name)
        config_manager.remove_feature(feature_name)
        print_fancy(f"Removed {found_model['name']} model configuration", color="green")
        sys.exit(0)

    if feature_name not in FEATURES:
        print_fancy(f"Unknown feature: {feature_name}", color="red")
        sys.exit(1)

    feature = get_feature(feature_name)
    
    if feature is None:
        print_fancy(f"Feature {feature_name} is not implemented", color="red")
        sys.exit(1)

    feature.disable()
    config_manager.remove_feature(feature_name)
