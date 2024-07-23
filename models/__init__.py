from enum import Enum
import os
import importlib
from typing import Type, Dict
from models.base_model import BaseModel


class ModelProvider(Enum):
    OPEN_AI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"

    
class ModelTag(Enum):
    MOST_INTELLIGENT = "most_intelligent"  # Tag for the most intelligent variant available for a provider
    BALANCED = "balanced"  # Tag for a model that is balanced in terms of cost and capability
    FASTEST = "fastest"  # Tag for a model that is fast but not necessarily the most intelligent

    
class TagSelectionMode(Enum):
    ANY = "any"
    ALL = "all"


MODELS: Dict[str, Type['BaseModel']] = {}
PROVIDER_NAMES = [provider.value for provider in ModelProvider]


def model(provider: ModelProvider, name, context_size, cost_per_thousand_input_tokens, vision_capability=False, tags=[]):
    """
    Decorator to register a model with the system.
    
    Args:
        provider (ModelProvider): The provider (company) of the model
        name (str): The name of the model
        context_size (int): The size of the context window
        cost_per_thousand_input_tokens (float): The cost per thousand input tokens
        vision_capability (bool): Whether the model has vision capability
        tags (list): A list of tags for the model
    """

    def decorator(cls):
        if issubclass(cls, BaseModel):
            MODELS[name] = cls
            cls.provider = provider
            cls.model_name = name
            cls.context_size = context_size
            cls.cost_per_thousand_input_tokens = cost_per_thousand_input_tokens
            cls.vision_capability = vision_capability
            cls.tags = [tag.value for tag in tags]
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
        # Make sure its a directory and not a file
        if not os.path.isdir(os.path.join(current_dir, subdir)):
            continue
        
        # Import the module
        importlib.import_module(f"{__name__}.{subdir}")


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


def find_models(provider: ModelProvider, vision_capability=None, min_context=None, lowest_cost=False, tags=[], tag_mode=TagSelectionMode.ALL):
    """
    Find models based on provider, vision capability, context size, and cost.
    
    Args:
        provider (ModelProvider): The provider to filter by
        vision_capability (bool): Whether the model has vision capability
        min_context (int): The minimum context size
        lowest_cost (bool): Whether to sort by lowest cost
        tags (list): A list of tags to filter by
        tag_mode (TagSelectionMode): The mode for filtering by tags
        
    Returns:
        list (str): A list of model names that match the criteria
    """
    
    model_names = [
        name for name, cls in MODELS.items() 
        if cls.provider.value == provider
        and (
            len(tags) == 0
            or (tag_mode == TagSelectionMode.ALL and all(tag in cls.tags for tag in tags))
            or (tag_mode == TagSelectionMode.ANY and any(tag in cls.tags for tag in tags))
        )
        and (
            vision_capability is None 
            or vision_capability is False
            or cls.vision_capability == vision_capability
        )
        and (
            min_context is None 
            or cls.context_size >= min_context
        )
    ]
    
    # Define a sorting algorithm that will sort by cost, then by vision capability, then by vision cost
    # The benefit of this is that we can sort by cost, but still have vision models first if vision is required
    # If vision is not required, we might also still consider vision models if they are cheaper than non-vision models
    def sort_weights(name):
        cls = MODELS[name]
        cost = cls.cost_per_thousand_input_tokens if lowest_cost else 0
        vision_sort = 0 if cls.vision_capability else 1  # Non-vision models first
        vision_cost = cls.cost_per_thousand_input_tokens if vision_capability in [None, False] and cls.vision_capability else 0
        return (cost, vision_sort, vision_cost)
    
    # Sort the list using the custom key
    sorted_model_names = sorted(model_names, key=sort_weights)
    
    return sorted_model_names
