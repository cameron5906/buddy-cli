#!/usr/bin/env python3
import sys
import os

# Add the current directory to the Python path to ensure modules can be found
sys.path.append(os.path.dirname(__file__))

from commands.use import use
from commands.remove import remove
from commands.info import display_info
from model_factory import ModelFactory

model_factory = ModelFactory()


def main():
    if len(sys.argv) < 2:
        print("Usage: buddy <command>")
        print("Type 'buddy info' for more information")
        sys.exit(1)

    command = sys.argv[1]

    # Check for non-intelligent commands
    if command == "info":
        display_info()
        sys.exit(0)
        
    elif command == "use":
        use(sys.argv[2:])
        sys.exit(0)
        
    elif command == "remove":
        remove(sys.argv[2:])
        sys.exit(0)
    
    # Load the configured model
    
    model = model_factory.get_model(require_vision=False)
    
    if command == "help":
        if len(sys.argv) < 3:
            print("Usage: buddy help <task>")
            sys.exit(1)
            
        query = " ".join(sys.argv[2:])
        model.execute_educational(query)
    
    elif command == "carefully":
        if len(sys.argv) < 3:
            print("Usage: buddy carefully <task>")
            sys.exit(1)
            
        query = " ".join(sys.argv[2:])
        model.execute_carefully(query)
    
    elif command == "explain":
        if len(sys.argv) < 3:
            print("Usage: buddy explain <command>")
            sys.exit(1)
            
        command_string = " ".join(sys.argv[2:])
        model.explain(command_string)
    
    else:
        query = " ".join(sys.argv[1:])
        model.execute_unsupervised(query)    


if __name__ == "__main__":
    main()
