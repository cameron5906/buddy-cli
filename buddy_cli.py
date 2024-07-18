import sys
from commands.use import use_feature
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
        use_feature(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
