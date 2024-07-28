import pandas as pd
from abilities.analysis.tiny_db import handle_analyze_structured_data
from utils.shell_utils import print_fancy


def handle_analyze_json(file_path, instructions):
    """
    Analyzes a JSON file based on provided instructions, returning the requested information.
    
    Args:
        file_path (str): The path to the JSON file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
    
    # Load file into a dataframe
    df = pd.read_json(file_path)
    
    print_fancy(f"Analyzing {file_path}: {instructions}", italic=True, color="cyan")
    
    return handle_analyze_structured_data(df, instructions)
