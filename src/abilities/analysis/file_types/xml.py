import pandas as pd

from abilities.analysis.tiny_db import handle_analyze_structured_data
from models import ModelTag
from models.base_model_factory import ModelFactory
from utils.shell_utils import print_fancy

def handle_analyze_xml(file_path, instructions):
    """
    Analyzes an XML file based on provided instructions, returning the requested information.
    
    Args:
        file_path (str): The path to the XML file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """

    # Use language model to determine the XPath selector    
    print_fancy(f"Parsing XML format...", color="cyan")
    xpath = __create_selector(file_path)
    
    if xpath is None:
        return "I'm not able to read through this file, it is too complex."
    
    # Load file into a dataframe
    df = pd.read_xml(file_path, xpath=xpath)
    
    print_fancy(f"Analyzing {file_path}: {instructions}", italic=True, color="cyan")
    return handle_analyze_structured_data(df, instructions)

def __create_selector(file_path):
    """
    Gives a file path, determines the appropriate XPath selector for the data.
    
    Args:
        file_path (str): The path to the XML file
        
    Returns:
        str | None: The XPath selector for the data, or None if it is too complex to figure out
    """
    
    model = ModelFactory().get_model(require_vision=False, tags=[ModelTag.MOST_INTELLIGENT])
    
    # Provide a snippet so it can deduce the structure
    file_snippet = open(file_path, "r").read()[:500]
    
    messages = [
        {
            "role": "system",
            "content": """
You will be provided with a snippet of the XML to view the structure of the data.
Your goal is to create a selector that will load the data into a pandas dataframe using the set_xpath tool.
If the data is too complex to create a selector, you will use your reject_file tool to inform the user.
"""
        },
        {
            "role": "user",
            "content": file_snippet
        }
    ]
    
    tools = [
        model.make_tool("set_xpath", "Sets the XPath to load the data into a pandas dataframe", {"xpath": "string"}, ["xpath"]),
        model.make_tool("reject_file", "Indicates that the file is too complex to analyze", {}, [])
    ]
    
    response = model.run_inference(messages=messages, tools=tools, temperature=0.0)
    
    call_id, call_args, _ = model.get_tool_call("set_xpath", response)
    if call_id is not None:
        return call_args["xpath"]
    
    return None