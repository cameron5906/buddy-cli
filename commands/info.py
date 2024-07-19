from config.config_manager import ConfigManager
from test.test___future__ import features


def display_info():
    """
    Displays information about the Buddy CLI.
    """

    config = ConfigManager()
    features = config.get_features()
    
    current_model = config.get_current_model()
    enabled_features = len(features) > 0 and ", ".join(features) or "None"
    
    info_text = f"""
    Buddy CLI - Command Line Utility powered by Generative AI

    Current Model: {current_model}
    Enabled Features: {enabled_features}

    Usage:
        buddy <task> - Execute a task in the shell without supervision
        buddy <command> [options] - Execute a Buddy command

    Commands:
        info                                Display this information
        help        <task>                  Work through a task collaboratively
        carefully   <task>                  Execute commands with confirmation on non-read operations
        explain     <command>               Provide an educational explanation of a command
        use         <feature> [arguments]   Configure Buddy to use a specific model or feature.

    Features:
        gpt4o <apiKey>    Configure Buddy to use OpenAI GPT-4 and save the specified API key.

    Examples:
        buddy what's my local IP address
        buddy carefully remove kubernetes
        buddy help me set up a Minecraft server
        buddy explain source ~/.bashrc
        buddy use gpt4o YOUR_API_KEY
        buddy use chrome
    """
    print(info_text)
