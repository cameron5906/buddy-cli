#!/usr/bin/env python3
import sys
import os

# Add the current directory to the Python path to ensure modules can be found
sys.path.append(os.path.dirname(__file__))

from commands.use import use_feature
from commands.info import display_info
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

    if command == "info":
        display_info()
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
