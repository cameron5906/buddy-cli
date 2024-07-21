import os
import importlib
from typing import Type, Dict
from abilities.base_ability import BaseAbility

ABILITIES: Dict[str, Type['BaseAbility']] = {}


def ability(name, description, argument_schema):
    """
    Decorator to register an ability with the system.
    This decoration will automatically register all action handlers on the class.
    
    Args:
        name (str): The name of the ability
        description (str): A description of the ability
        argument_schema (dict): The parameter schema for the ability when called (name: type)
    """

    def decorator(cls: Type['BaseAbility']):
        if not issubclass(cls, BaseAbility):
            raise TypeError("Class must inherit from BaseAbility")

        # Add metadata to the class
        cls.ability_name = name
        cls.description = description
        cls.argument_schema = argument_schema

        # Automatically discovering and registering actions defined on the class
        cls.actions = []
        cls.action_handlers = {}
        
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, '_action_name'):  # Check if this is an action
                cls.actions.append({
                    "name": f"{name}_{attr._action_name}",
                    "description": attr._action_description,
                    "argument_schema": attr._action_argument_schema,
                    "required_arguments": attr._action_required_arguments
                })
                
                cls.action_handlers[attr._action_name] = attr._handler

        ABILITIES[name] = cls

        return cls

    return decorator


def ability_action(name, description, argument_schema, required_arguments=None):
    """
    Used to decorate methods on an ability to register them as actions to be called by the model.
    
    Args:
        name (str): The name of the action
        description (str): A description of the action
        argument_schema (dict): The parameter schema for the action when called (name: type)
        required_arguments (list): A list of required arguments for the action
    """

    def decorator(func):
        # Attach metadata directly to the function
        setattr(func, '_action_name', name)
        setattr(func, '_action_description', description)
        setattr(func, '_action_argument_schema', argument_schema)
        setattr(func, '_action_required_arguments', required_arguments or [])

        # Define a wrapper that acts as the decorated function
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Preserve metadata through the wrapper
        wrapper._action_name = func._action_name
        wrapper._action_description = func._action_description
        wrapper._action_argument_schema = func._action_argument_schema
        wrapper._action_required_arguments = func._action_required_arguments
        wrapper._handler = func
        
        return wrapper

    return decorator


def discover_abilities():
    # Get directories in this file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
    
    # Iterate over each directory
    for subdir in subdirs:
        # Import the module
        importlib.import_module(f"{__name__}.{subdir}")


def get_ability(name, *args, **kwargs):
    """
    Get an instance of the ability by name.
    
    Args:
        name (str): The name of the ability
        *args: Positional arguments to pass to the ability class
        **kwargs: Keyword arguments to pass to the ability class
    
    Returns:
        BaseAbility: An instance of the ability class, or None if not found
    """
    ability_cls = ABILITIES.get(name)
    if not ability_cls:
        return None
    
    return ability_cls(*args, **kwargs)
