import sys
from commands.use import use_feature
from commands.help import display_help
from commands.carefully import execute_with_confirmation
from config.config_manager import ConfigManager
from config.secure_store import SecureStore
from models.gpt4o import GPT4OModel

def generate_command(query):
    model = GPT4OModel()
    return model.generate_command(query)

def main():
    config_manager = ConfigManager()
    secure_store = SecureStore()
    
    if len(sys.argv) < 2:
        print("Usage: buddy <command> [options]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "help":
        display_help()
    elif command == "carefully":
        if len(sys.argv) < 3:
            print("Usage: buddy carefully <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        shell_command = generate_command(query)
        execute_with_confirmation(shell_command)
    elif command == "use":
        use_feature(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
