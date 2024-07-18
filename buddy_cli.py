import sys
from config.config_manager import ConfigManager
from config.secure_store import SecureStore

def main():
    config_manager = ConfigManager()
    secure_store = SecureStore()
    
    if len(sys.argv) < 2:
        print("Usage: buddy <command> [options]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "help":
        print("Display help information.")
        # Future: Route to help command
    elif command == "carefully":
        print("Execute commands with confirmation.")
        # Future: Route to carefully command
    elif command == "use":
        if len(sys.argv) < 4:
            print("Usage: buddy use <feature> <value>")
            sys.exit(1)
        feature = sys.argv[2]
        value = sys.argv[3]
        if feature == "gpt4o":
            secure_store.set_api_key("gpt4o", value)
            config_manager.set_current_model("gpt4o")
        elif feature == "chrome":
            config_manager.add_feature("chrome")
        print(f"Configured {feature} with value {value}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
