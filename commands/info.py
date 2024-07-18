def display_info():
    info_text = """
    Buddy CLI - Command Line Utility for Generative AI

    Usage:
        buddy <command> [options]

    Commands:
        info          Display this information
        help          Work through a task collaboratively
        carefully     Execute commands with confirmation.
        use <feature> [value]  Configure Buddy to use a specific model or feature.

    Features:
        gpt4o <apiKey>    Configure Buddy to use OpenAI GPT-4 and save the specified API key.
        chrome            Configure Buddy to use headless Chrome browser (Selenium) for web research.

    Examples:
        buddy use gpt4o YOUR_API_KEY
        buddy use chrome
    """
    print(info_text)
