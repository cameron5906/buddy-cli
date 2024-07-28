import os
import pandas as pd
from abilities.analysis.tiny_db import handle_analyze_structured_data
from models import ModelTag
from utils.shell_utils import print_fancy
from models.base_model_factory import ModelFactory


def handle_analyze_spreadsheet(file_path, instructions):
    """
    Analyzes a spreadsheet file and returns the requested information.

    Args:
        file_path (str): The path to the spreadsheet file
        instructions (str): Detailed instructions for what information to retrieve

    Returns:
        str: The analysis results
    """
    
    print_fancy(f"Opening spreadsheet file: {file_path}: {instructions}", italic=True, color="cyan")
    
    print_fancy("Parsing spreadsheet format...", italic=True, color="cyan")
    
    delimiter, quote_character = __get_spreadsheet_parsing_params(file_path)
    file_ext = os.path.splitext(file_path)[1]
    
    if delimiter is None:
        delimiter = ","
        
    if quote_character is None:
        quote_character = '"'
        
    # Load the spreadsheet data into a DataFrame
    if file_ext == ".csv":
        df = pd.read_csv(file_path, delimiter=delimiter, quotechar=quote_character, skipinitialspace=True,skip_blank_lines=True)
    elif file_ext == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        return "I'm sorry, I can't analyze this type of file. I only work with CSV and Excel files."
    
    print_fancy(f"Analyzing {file_path}: {instructions}", italic=True, color="cyan")
    
    return handle_analyze_structured_data(df, instructions)
    
def __get_spreadsheet_parsing_params(file_path):
    """
    Determines the appropriate parsing parameters for the spreadsheet data.

    Args:
        file_path (str): The path to the spreadsheet file

    Returns:
        dict: The parsing parameters for the spreadsheet data
    """
    
    model = ModelFactory().get_model(require_vision=False, tags=[ModelTag.MOST_INTELLIGENT])
    
    # Provide a snippet so it can deduce the structure
    file_snippet = open(file_path, "r").read()[:500]
    
    messages = [
        {
            "role": "system",
            "content": """
You will analyze the spreadsheet snippet to determine the appropriate parameters for parsing the data.
The parameters that need to be found are the delimiter between columns and the quote character used in the data - defaulted to ".
"""
        },
        {
            "role": "user",
            "content": file_snippet
        }
    ]
    
    tools = [
        model.make_tool("set_parsing_params", "Sets the parsing parameters for the spreadsheet data", {"delimiter": "string", "quote_character": "string"}, ["delimiter", "quote_character"]),
        model.make_tool("reject_file", "Indicates that the file could not be analyzed")
    ]
    
    response = model.run_inference(messages=messages, tools=tools, temperature=0.0, require_tool_usage=True)
    
    parsing_params_call, parsing_args, _ = model.get_tool_call("set_parsing_params", response)
    if parsing_params_call is None:
        return None, None
    
    return parsing_args["delimiter"], parsing_args["quote_character"]