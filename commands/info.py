import initialize_modules
from features import FEATURES
from models import MODELS
from config.config_manager import ConfigManager


def display_info():
    """
    Displays information about the Buddy CLI.
    """

    config = ConfigManager()

    all_models = [name for name, _ in MODELS.items()]    
    current_model = config.get_current_model()

    enabled_features = config.get_features()
    all_features = [name for name, _ in FEATURES.items()]
    
    enabled_features_str = ", ".join(enabled_features) if len(enabled_features) > 0 else "None"
    disabled_features_str = ", ".join([feature for feature in all_features if feature not in enabled_features]) if len(enabled_features) < len(all_features) else "None"
    
    info_text = f"""
    Buddy CLI - Command Line Utility powered by Generative AI

    Configuration:
        Current Model: {current_model}
        Available Models: {", ".join(all_models)}
        Enabled Features: {enabled_features_str}
        Available Features: {disabled_features_str}

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


if __name__ == "__main__":
    display_info()
