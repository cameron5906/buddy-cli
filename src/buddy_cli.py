#!/usr/bin/env python3
import sys
import os

import initialize_flows
from flows import get_flow_name, create_flow
from models import ModelTag

# Add the current directory to the Python path to ensure modules can be found
sys.path.append(os.path.dirname(__file__))

from commands.install import install
from commands.use import use
from commands.remove import remove
from commands.info import display_info
from models.base_model_factory import ModelFactory

model_factory = ModelFactory()

def handle_unknown_operation():
    print("Usage: buddy <command>")
    print("Type 'buddy info' for more information")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        handle_unknown_operation()

    suffix_str = " ".join(sys.argv[1:])
    command = sys.argv[1]

    # Installation as a shell alias
    if command == "install":
        install(sys.argv[2:])
        sys.exit(0)

    # Buddy information and current configuration
    elif command == "info":
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
    model = model_factory.get_model(require_vision=False, tags=[ModelTag.BALANCED])
    
    flow_name = get_flow_name(suffix_str)

    if flow_name is None:
        handle_unknown_operation()
    
    if flow_name != "__default":
        flow_command_str = suffix_str[len(flow_name):].strip()
    else:
        flow_command_str = suffix_str
        
    flow = create_flow(flow_name, model)
    
    flow.execute(flow_command_str)


if __name__ == "__main__":
    main()
