import importlib
import os
from typing import Dict, List, Type, Union
from flows.base_flow import BaseFlow
from models.base_model import BaseModel
from utils.shell_utils import print_fancy

FLOWS: Dict[str, Type['BaseFlow']] = {}

def flow(prefix: Union[str, List[str], None] = None):
    """
    Decorator to register a flow with the system.
    
    Args:
        prefix (Union[str, List[str], None]): The prefix for the flow (what comes after "buddy")
    """

    def decorator(cls):
        if issubclass(cls, BaseFlow):
            prefix_list = []
            
            if isinstance(prefix, str):
                prefix_list.append(prefix)
            elif isinstance(prefix, list):
                prefix_list.extend(prefix)
            else:
                prefix_list.append("__default")
            
            for name in prefix_list:
                if name in FLOWS:
                    if name == "__default":
                        raise ValueError("Default flow already registered")
                    
                    raise ValueError(f"Flow with prefix {name} already registered")
                
                FLOWS[name] = cls
        else:
            raise TypeError("Flow must inherit from BaseFlow")
        
        return cls

    return decorator

def discover_flows():
    # Get directories in this file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir_files = os.listdir(current_dir)
    
    # Iterate over each file and import it
    for file in current_dir_files:
        # Make sure its a file and not a directory
        if os.path.isdir(os.path.join(current_dir, file)):
            continue
        
        # Make sure its a python file and not a base file
        if not file.endswith(".py") or file == "__init__.py" or file.startswith("base_"):
            continue
        
        # Get the base name without extension
        base_name = os.path.splitext(file)[0]
        
        # Import the module
        importlib.import_module(f"{__name__}.{base_name}")
        
def create_flow(name: Union[str, None], model: BaseModel, *args, **kwargs) -> BaseFlow:
    """
    Get an instance of a flow by name
    
    Args:
        model (BaseModel): The model to use for the flow
    """
    
    if name is None:
        name = "__default"
    
    if name not in FLOWS:
        if name == "__default":
            raise ValueError("Default flow not found")
        
        raise ValueError(f"Flow with name {name} not found")
    
    return FLOWS[name](model, *args, **kwargs)

def get_flow_name(arg_str: str) -> Union[str, None]:
    """
    Get the flow name from the argument string
    
    Args:
        arg_str (str): The argument string
    
    Returns:
        str: The flow name, or None if not found
    """
    
    for prefix in FLOWS:
        if arg_str.startswith(prefix):
            return prefix
        
    if "__default" in FLOWS:
        return "__default"
    else:
        print_fancy("WARNING: No default flow found", bold=True, color="yellow")
        
    return None