from config.config_manager import ConfigManager
from config.secure_store import SecureStore

def use_feature(args):
    config_manager = ConfigManager()
    secure_store = SecureStore()

    if len(args) < 1:
        print("Usage: buddy use <feature> [value]")
        return

    feature = args[0]
    value = args[1] if len(args) > 1 else None

    if feature == "gpt4o":
        if not value:
            print("Usage: buddy use gpt4o <apiKey>")
            return
        secure_store.set_api_key("gpt4o", value)
        config_manager.set_current_model("gpt4o")
    elif feature == "chrome":
        config_manager.add_feature("chrome")
    else:
        print(f"Unknown feature: {feature}")
        return

    print(f"Configured {feature} with value {value}" if value else f"Configured {feature}")
