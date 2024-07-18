from config.config_manager import ConfigManager
from config.secure_store import SecureStore

def use_feature(feature, value):
    config_manager = ConfigManager()
    secure_store = SecureStore()

    if feature == "gpt4o":
        secure_store.set_api_key("gpt4o", value)
        config_manager.set_current_model("gpt4o")
    elif feature == "chrome":
        config_manager.add_feature("chrome")
    else:
        print(f"Unknown feature: {feature}")
        return

    print(f"Configured {feature} with value {value}")
