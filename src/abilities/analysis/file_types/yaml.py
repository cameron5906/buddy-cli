import yaml
import pandas as pd

from abilities.analysis.tiny_db import handle_analyze_structured_data
from utils.shell_utils import print_fancy


def handle_analyze_yaml(file_path, instructions):
    """
    Analyzes a YAML file based on provided instructions, returning the requested information.
    
    Args:
        file_path (str): The path to the YAML file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
    
    # Load file into a dataframe
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        df = pd.json_normalize(data)
    
        print_fancy(f"Analyzing {file_path}: {instructions}", italic=True, color="cyan")
        
        return handle_analyze_structured_data(df, instructions)
