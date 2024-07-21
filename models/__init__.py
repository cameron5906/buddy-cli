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
PROVIDER_NAMES = [provider.value for provider in ModelProvider]


def model(provider: ModelProvider, name, context_size, cost_per_thousand_input_tokens, vision_capability=False):
    """
    Decorator to register a model with the system.
    
    Args:
        provider (ModelProvider): The provider (company) of the model
        name (str): The name of the model
        context_size (int): The size of the context window
        cost_per_thousand_input_tokens (float): The cost per thousand input tokens
        vision_capability (bool): Whether the model has vision capability
    """

    def decorator(cls):
        if issubclass(cls, BaseModel):
            MODELS[name] = cls
            cls.provider = provider
            cls.model_name = name
            cls.context_size = context_size
            cls.cost_per_thousand_input_tokens = cost_per_thousand_input_tokens
            cls.vision_capability = vision_capability
        else:
            raise TypeError("Model must inherit from BaseModel")
        return cls

    return decorator


def discover_models():
    # Get directories in this file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
    
    # Iterate over each directory
    for subdir in subdirs:
        # Import the module
        module = importlib.import_module(f"{__name__}.{subdir}")
        
        # Iterate over directory contents to import each model
        for name in dir(module):
            if "__" in name or name.startswith("base_"):
                continue
            
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, BaseModel):
                importlib.import_module(f"{__name__}.{subdir}.{name}")


def create_model(name, *args, **kwargs):
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


def find_models(provider: ModelProvider, vision_capability=None, min_context=None, lowest_cost=False):
    """
    Find models based on provider, vision capability, context size, and cost.
    
    Args:
        provider (ModelProvider): The provider to filter by
        vision_capability (bool): Whether the model has vision capability
        min_context (int): The minimum context size
        lowest_cost (bool): Whether to sort by lowest cost
        
    Returns:
        list (str): A list of model names that match the criteria
    """
    
    model_names = [
        name for name, cls in MODELS.items() 
        if cls.provider == provider 
        and (
            vision_capability is None 
            or cls.vision_capability == vision_capability
        )
        and (
            min_context is None 
            or cls.context_size >= min_context
        )
    ]
    
    if lowest_cost:
        model_names.sort(key=lambda name: MODELS[name].cost_per_thousand_input_tokens)
        
    return model_names
