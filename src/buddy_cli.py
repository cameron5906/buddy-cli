#!/usr/bin/env python3
import sys
import os

# Add the current directory to the Python path to ensure modules can be found
sys.path.append(os.path.dirname(__file__))

from commands.install import install
from commands.use import use
from commands.remove import remove
from commands.info import display_info
from models.base_model_factory import ModelFactory

model_factory = ModelFactory()


def main():
    if len(sys.argv) < 2:
        print("Usage: buddy <command>")
        print("Type 'buddy info' for more information")
        sys.exit(1)

    command = sys.argv[1]

    # Installation as a shell alias
    if command == "install":
        install(sys.argv[2:])
        sys.exit(0)

    # Buddy information and current configuration
    if command == "info":
        display_info(sys.argv[2:])
        sys.exit(0)
        
    # Enablement of model APIs or abilities
    elif command == "use":
        use(sys.argv[2:])
        sys.exit(0)
        
    # Removal of model APIs or abilities
    elif command == "remove":
        remove(sys.argv[2:])
        sys.exit(0)
    
    # Find a model to use for this command
    model = model_factory.get_model(require_vision=False)
    
    # Collaborative educational flow
    if command == "help":
        if len(sys.argv) < 3:
            print("Usage: buddy help <task>")
            sys.exit(1)
            
        query = " ".join(sys.argv[2:])
        model.execute_educational(query)
    
    # Supervised flow for non-read operations
    elif command == "carefully":
        if len(sys.argv) < 3:
            print("Usage: buddy carefully <task>")
            sys.exit(1)
            
        query = " ".join(sys.argv[2:])
        model.execute_carefully(query)
    
    # Explanation of a command
    elif command == "explain":
        if len(sys.argv) < 3:
            print("Usage: buddy explain <command>")
            sys.exit(1)
            
        command_string = " ".join(sys.argv[2:])
        model.explain(command_string)
    
    # Unsupervised flow
    else:
        query = " ".join(sys.argv[1:])
        model.execute_unsupervised(query)    


if __name__ == "__main__":
    main()
