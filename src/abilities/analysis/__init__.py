import os
from abilities import ability, ability_action
from abilities.analysis.file_types.images import handle_analyze_image
from abilities.analysis.file_types.json import handle_analyze_json
from abilities.analysis.file_types.pdf import handle_analyze_pdf
from abilities.analysis.file_types.spreadsheets import handle_analyze_spreadsheet
from abilities.analysis.file_types.xml import handle_analyze_xml
from abilities.analysis.file_types.yaml import handle_analyze_yaml
from abilities.base_ability import BaseAbility
from abilities.analysis.utils import is_poppler_installed, install_poppler
from abilities.analysis.locate_file import handle_locate_file
from utils.shell_utils import print_fancy

@ability("analysis", "Analyze a variety of documents and images", {})
class Analysis(BaseAbility):

    def enable(self, args=None):
        if not is_poppler_installed():
            print_fancy("Poppler wasn't found on this system", bold=True, color="yellow")
            install_poppler()
            
            if not is_poppler_installed():
                print_fancy("Failed to install poppler", bold=True, color="red")
                return False
    
    def disable(self):
        return super().disable()
    
    def get_prompt(self):
        return """
# File Analysis
When asked about a file's contents, you will use the analyze_file tool to request an expert to analyze the file. You will provide the tool with detailed instructions on what information is being requested.
Your instructions for the expert will be based on the user's query, which you will not modify or expand upon. The instructions must contain the same constraints as the user specified.
You will not refer to the file or file extension in your instructions - you will refer to it as 'the data' only. The expert does not concern themselves with the file name or its extension.
Use the locate_file tool to find the file if an exact file name is not provided. If a filename is provided, you will use it.

When you have the results from the expert, you will relay them back to the user. You will be detailed in your response and will avoid responding with 'Information extracted', 'Extracted 10 rows', etc. You will provide the user with the information they requested.
"""
    
    @ability_action(
        "locate_file",
        "Used to locate the absolute path to the file being referenced by the user",
        {
            "file_name": {
                "type": "string",
                "description": "The assumed name of the file"
            }
        },
        ["file_name"]
    )
    def locate_file(self, args):
        return handle_locate_file(args["file_name"])
    
    @ability_action(
        "analyze_file",
        "Request an expert to look at a file and derive information from it.",
        {
            "file_path":{
                "type": "string",
                "description": "The absolute path to the file"    
            },
            "instructions": {
                "type": "string",
                "description": "Detailed instructions to pass to the analysis expert"
            }
        },
        ["file_path", "instructions"]
    )
    def analyze_file(self, args):
        """
        Validates the file exists and that it is supported. Uses the proper analysis function based on the file type.

        Args:
            args (dict): The arguments for the analysis from the model

        Returns:
            str: The analysis results
        """
        
        file_path = os.path.basename(args["file_path"])
        
        if not os.path.exists(file_path):
            return f"I'm sorry, I couldn't find the file {file_path}. You should use the locate_file tool to find the file first."
        else:
            file_path = os.path.abspath(file_path)
        
        instructions = args["instructions"]
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in [".pdf"]:
            answer = handle_analyze_pdf(file_path, instructions)
        elif ext in [".csv", ".xlsx"]:
            answer =  handle_analyze_spreadsheet(file_path, instructions)
        elif ext in [".jpg", ".jpeg", ".png"]:
            answer =  handle_analyze_image(file_path, instructions)
        elif ext in [".json"]:
            answer =  handle_analyze_json(file_path, instructions)
        elif ext in [".yaml", ".yml"]:
            answer =  handle_analyze_yaml(file_path, instructions)
        elif ext in [".xml"]:
            answer =  handle_analyze_xml(file_path, instructions)
        else:
            return "I'm sorry, I don't know how to analyze that file type. It's unsupported."

        answer = f"""
Expert analysis of the data:

{answer}

You must provide the user with this information.
"""
        
        return answer