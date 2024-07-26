import pandas as pd
from abilities.analysis.tinydb_util import query_pandas_data_frame


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
    
    return query_pandas_data_frame(df, instructions)
