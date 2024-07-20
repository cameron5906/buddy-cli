from enum import Enum
import os
import importlib
from typing import Type, Dict
from base_model import BaseModel


class ModelProvider(Enum):
    OPEN_AI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"

    
MODELS: Dict[str, Type['BaseModel']] = {}


def model(provider: ModelProvider, name, context_size, vision_capability=False):
    """
    Decorator to register a model with the system.
    
    Args:
        provider (ModelProvider): The provider (company) of the model
        name (str): The name of the model
        context_size (int): The size of the context window
        vision_capability (bool): Whether the model has vision capability
    """

    def decorator(cls):
        if issubclass(cls, BaseModel):
            MODELS[name] = cls
            cls.provider = provider
            cls.model_name = name
            cls.context_size = context_size
            cls.vision_capability = vision_capability
        else:
            raise TypeError("Model must inherit from BaseModel")
        return cls

    return decorator


def discover_models():
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith(".py") and file != "__init__.py" and not file.startswith("base_"):
            module_name = f"models.{file[:-3]}"
            importlib.import_module(module_name)


def get_model(name, *args, **kwargs):
    """
    Get an instance of a model by name
    
    Args:
        name (str): The name of the model
        *args: Positional arguments to pass to the model class
        **kwargs: Keyword arguments to pass to the model class
    
    Returns:
        BaseModel: An instance of the model class, or None if not found
    """
    model_cls = MODELS.get(name)
    if not model_cls:
        return None
    
    return model_cls(*args, **kwargs)
