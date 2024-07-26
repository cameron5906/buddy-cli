import os
import sys
from models.base_model_factory import ModelFactory
from utils.shell_utils import print_fancy


def handle_locate_file(file_reference):
    """
    Looks in the current directory for a referenced file. If not found, allow the user to specify the path to the file.

    Args:
        file_name (str): The name parsed by the model, which may or may not be the exact file name
    
    Returns:
        str | None: The absolute path to the file, or None if not found
    """
    
    # Attempt #1: Check if the file exists in the current working directory
    if os.path.exists(file_reference):
        # Return the absolute path to the file
        return os.path.abspath(file_reference)
    
    # Get a directory listing for the working directory
    files = os.listdir(os.getcwd())
    files_str = "\n".join(files)
    
    # Attempt #2: Use a model to attempt to match the correct file name
    model = ModelFactory().get_model(require_vision=False, lowest_cost=True)

    if model is not None:
        messages = [
            {
                "role": "system",
                "content": """
You will select the name of the file that matches the query provided by the user by using the select_file tool.
You will only use select_file if you have high confidence that it is the one the user is referring to.
If you do not feel confident about the selection, you will use your file_not_found tool to inform the user that you could not locate the file.
"""
            },
            {
                "role": "assistant",
                "content": f"""
The current directory contains the following files:
{files_str}             
"""
            },
            {
                "role": "user",
                "content": file_reference
            }
        ]
        tools = [
            model.make_tool("select_file", "Chooses the file that matches the query", {"file_name": "string"}, ["file_name"]),
            model.make_tool("file_not_found", "Indicates that the file could not be located", {}, [])
        ]
        
        response = model.run_inference(messages=messages, tools=tools, temperature=0.0)
        
        # Check if the model selected a file
        select_file_call_id, select_file_args, _ = model.get_tool_call("select_file", response)
        if select_file_call_id is not None:
            full_path = os.path.abspath(select_file_args["file_name"])
            print_fancy(f"Selected file: {full_path}", color="green")
            return full_path
    
    # Attempt #3: Ask the user to provide the path to the file
    print_fancy(f"Could not locate the file {file_reference}. Please provide the absolute path to the file.", color="yellow")
    file_path = input("File path: ")
    
    # Check if the file exists
    if os.path.exists(file_path):
        return file_path
    
    print_fancy(f"Could not locate the file at the path {file_path}.", color="red")
    sys.exit(1)
