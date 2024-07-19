import initialize_features
from features import FEATURES
from config.config_manager import ConfigManager


def display_info():
    """
    Displays information about the Buddy CLI.
    """

    config = ConfigManager()
    features = config.get_features()
    print(f"Debug: features from config = {features}")  # Debugging line
    
    current_model = config.get_current_model()
    print(f"Debug: current model = {current_model}")  # Debugging line
    
    all_features = [name for name, _ in FEATURES.items()]
    print(f"Debug: all features = {all_features}")  # Debugging line
    
    enabled_features = ", ".join(features) if len(features) > 0 else "None"
    disabled_features = ", ".join([feature for feature in all_features if feature not in features]) if len(features) < len(all_features) else "None"
    
    info_text = f"""
    Buddy CLI - Command Line Utility powered by Generative AI

    Configuration:
        Current Model: {current_model}
        Enabled Features: {enabled_features}
        Available Features: {disabled_features}

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
