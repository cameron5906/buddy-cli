#!/usr/bin/env python3
import sys
import os

# Add the current directory to the Python path to ensure modules can be found
sys.path.append(os.path.dirname(__file__))

from commands.use import use_feature
from commands.info import display_info
from models.gpt4o import GPT4OModel


def main():
    if len(sys.argv) < 2:
        print("Usage: buddy <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "info":
        display_info()
    elif command == "help":
        if len(sys.argv) < 3:
            print("Usage: buddy help <task>")
            sys.exit(1)
            
        model = GPT4OModel()    
        query = " ".join(sys.argv[2:])
        model.execute_educational(query)
    elif command == "carefully":
        if len(sys.argv) < 3:
            print("Usage: buddy carefully <task>")
            sys.exit(1)
        model = GPT4OModel()    
        query = " ".join(sys.argv[2:])
        model.execute_carefully(query)
    elif command == "use":
        use_feature(sys.argv[2:])
    else:
        model = GPT4OModel()
        query = " ".join(sys.argv[1:])
        model.execute_unsupervised(query)    


if __name__ == "__main__":
    main()
