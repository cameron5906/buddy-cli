import os
import importlib
from typing import Type, Dict
from base_ability import BaseAbility

ABILITIES: Dict[str, Type['BaseAbility']] = {}


def ability(name, description, argument_schema):
    """
    Decorator to register an ability with the system.
    
    Args:
        name (str): The name of the ability
        description (str): A description of the ability
        argument_schema (dict): The parameter schema for the ability when called (name: type)
    """

    def decorator(cls):
        if issubclass(cls, BaseAbility):
            ABILITIES[name] = cls
            cls.description = description
            cls.argument_schema = argument_schema
        else:
            raise TypeError("Ability must inherit from BaseAbility")
        return cls

    return decorator


def discover_abilities():
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"abilities.{file[:-3]}"
            importlib.import_module(module_name)


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
