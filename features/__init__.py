import os
import importlib
from typing import Type, Dict
from base_feature import BaseFeature

FEATURES: Dict[str, Type['BaseFeature']] = {}


def feature(name, description, argument_schema):
    """
    Decorator to register a feature with the system.
    
    Args:
        name (str): The name of the feature
        description (str): A description of the feature
        argument_schema (dict): The parameter schema for the feature when called (name: type)
    """

    def decorator(cls):
        if issubclass(cls, BaseFeature):
            FEATURES[name] = cls
            cls.description = description
            cls.argument_schema = argument_schema
        else:
            raise TypeError("Feature must inherit from BaseFeature")
        return cls

    return decorator


def discover_features():
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"features.{file[:-3]}"
            importlib.import_module(module_name)


def get_feature(name, *args, **kwargs):
    """
    Get an instance of the feature by name.
    
    Args:
        name (str): The name of the feature
        *args: Positional arguments to pass to the feature class
        **kwargs: Keyword arguments to pass to the feature class
    
    Returns:
        BaseFeature: An instance of the feature class, or None if not found
    """
    feature_cls = FEATURES.get(name)
    if not feature_cls:
        return None
    
    return feature_cls(*args, **kwargs)
