import initialize_models
from abilities import ABILITIES
from models import MODELS, PROVIDER_NAMES, find_models
from config.config_manager import ConfigManager


def display_info(args):
    """
    Displays information about the Buddy CLI.
    """

    config = ConfigManager()

    if len(args) == 0:
        __print_main_instructions(config)
        return
    
    info_type = args[0]
    
    if info_type == "providers":
        __print_providers_info(config)
    elif info_type == "abilities":
        __print_abilities_info(config)
    else:
        print("Usage: buddy info [providers/abilities]")
        

def __print_main_instructions(config):
    """
    Prints the current configuration and usage instructions for the Buddy CLI.
    """

    current_model_provider = config.get_current_model_provider()

    enabled_abilities = config.get_abilities()
    enabled_abilities_str = ", ".join(enabled_abilities) if len(enabled_abilities) > 0 else "None"
    
    glossary_text = f"""
Buddy CLI - Command Line Utility powered by Generative AI

Configuration:
    Current Model Provider: {current_model_provider}
    Enabled Abilities: {enabled_abilities_str}

Usage:
    buddy <task>                        - Execute a task in the shell without supervision
    buddy <command> [options]           - Execute a Buddy command
    buddy info                          - Display this information
    buddy info providers                - Display information about available model providers and supported models
    buddy info abilities                - Display information about available abilities
    buddy info commands                 - Display information about available commands
    buddy use provider <name> [api_key] - Configure Buddy to use a model provider
    buddy use ability <name>            - Enable an ability

Examples:
    buddy what's my local IP address            - Get your local IP address without supervision
    buddy carefully remove kubernetes           - Remove Kubernetes resources with supervision
    buddy help me set up a Minecraft server     - Collaboratively set up a Minecraft server with Buddy
    buddy explain source ~/.bashrc              - Explain what 'source ~/.bashrc' does
    buddy use provider openai <api_key>         - Configure Buddy to use OpenAI
    buddy use ability browsing                  - Enable the browsing ability
    """
    
    print(glossary_text)


def __print_providers_info(config):
    """
    Prints information about available model providers and supported models.
    """
    
    current_model_provider = config.get_current_model_provider()
    
    provider_strings = []
    
    for provider_name in PROVIDER_NAMES:
        models = find_models(provider_name)
        
        if len(models) == 0:
            models_str = "None"
        else:
            models_str = "\n        ".join(models)
        
        provider_string = f"""{provider_name}
        {models_str}
"""
        
        provider_strings.append(provider_string)
 
    overview_str = "\n".join(provider_strings)
    
    providers_text = f"""
Buddy CLI - Command Line Utility powered by Generative AI

Model Providers are services that provide APIs that provide AI models for Buddy to use. You can configure Buddy to use a specific model provider using the 'buddy use provider <name> [api_key]' command.

Current Model Provider: {current_model_provider}

Available Model Providers and Supported Models:
{overview_str}
"""

    print(providers_text)

    
def __print_abilities_info(config):
    """
    Prints information about available abilities.
    """
    
    enabled_abilities = config.get_abilities()
    all_abilities = [name for name, _ in ABILITIES.items()]
    
    enabled_abilities_str = "\n     ".join(enabled_abilities) if len(enabled_abilities) > 0 else "None"
    disabled_abilities_str = "\n    ".join([ability for ability in all_abilities if ability not in enabled_abilities]) if len(enabled_abilities) < len(all_abilities) else "None"
    
    abilities_text = f"""
Buddy CLI - Command Line Utility powered by Generative AI

Abilities are features that Buddy can use to assist you in your tasks. You can enable or disable abilities using the 'buddy use ability <name>' and 'buddy remove ability <name>' commands.

Enabled Abilities:
    {enabled_abilities_str}
    
Available Abilities:
    {disabled_abilities_str}
"""

    print(abilities_text)


if __name__ == "__main__":
    display_info()
