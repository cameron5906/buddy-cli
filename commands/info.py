import initialize_modules
from abilities import ABILITIES
from models import MODELS
from config.config_manager import ConfigManager


def display_info():
    """
    Displays information about the Buddy CLI.
    """

    config = ConfigManager()

    all_models = [name for name, _ in MODELS.items()]    
    current_model = config.get_current_model()

    enabled_abilities = config.get_abilities()
    all_abilities = [name for name, _ in ABILITIES.items()]
    
    enabled_abilities_str = ", ".join(enabled_abilities) if len(enabled_abilities) > 0 else "None"
    disabled_abilities_str = ", ".join([ability for ability in all_abilities if ability not in enabled_abilities]) if len(enabled_abilities) < len(all_abilities) else "None"
    
    info_text = f"""
Buddy CLI - Command Line Utility powered by Generative AI

Configuration:
    Current Model: {current_model}
    Available Models: {", ".join(all_models)}
    Enabled Abilities: {enabled_abilities_str}
    Available Abilities: {disabled_abilities_str}

Usage:
    buddy <task> - Execute a task in the shell without supervision
    buddy <command> [options] - Execute a Buddy command

Commands:
    info                                            Display this information
    help        <task>                              Work through a task collaboratively
    carefully   <task>                              Execute commands with confirmation on non-read operations
    explain     <command>                           Provide an educational explanation of a command
    use         <model/ability> <name> [arguments]  Configure Buddy to use a specific model or ability
    remove      <model/ability> <name>              Remove a model or ability from Buddy

Models:
    gpt-4o       <apiKey>                            Configure Buddy to use OpenAI GPT-4 and save the specified API key

Abilities:


Examples:
    buddy what's my local IP address
    buddy carefully remove kubernetes
    buddy help me set up a Minecraft server
    buddy explain source ~/.bashrc
    buddy use gpt4o YOUR_API_KEY
    buddy use chrome
    """
    print(info_text)


if __name__ == "__main__":
    display_info()
