import os
from abilities import ability, ability_action
from abilities.analysis.analyzers.image_analysis import handle_analyze_image
from abilities.analysis.analyzers.spreadsheet_analysis import handle_analyze_spreadsheet
from abilities.analysis.analyzers.xml_analysis import handle_analyze_xml
from abilities.analysis.analyzers.yaml_analysis import handle_analyze_yaml
from abilities.base_ability import BaseAbility
from abilities.analysis.utils import is_poppler_installed, install_poppler
from abilities.analysis.locate_file import handle_locate_file
from utils.shell_utils import print_fancy
from abilities.analysis.analyzers.pdf_analysis import handle_analyze_pdf
from abilities.analysis.analyzers.json_analysis import handle_analyze_json

ARGUMENTS = {"file_path": "string", "instructions": {"type": "string", "description": "Detailed instructions to pass to the analysis expert"}}
REQUIRED_ARGUMENTS = ["file_path", "instructions"]


@ability("analysis", "Analyze images, spreadsheets, and other files", {})
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
You are able to speak to several experts who can analyze a variety of files for you on behalf of the user. You will not be analyzing these files yourself.
Your job is to format instructions that can be understood by the expert and pass them along with the file to be analyzed.
If an exact file name is not provided, you will use the locate_file tool to find the file.
You will not perform any prerequisite steps to analyze, modify, or prepare the file in any way. You are just the messenger.
You will provide the information back to the user in a format that aligns with the instructions they provided.

# Rules for Analyzing Files
## Creating Instructions
You will pass the user's request directly along to the expert, only modifying it if you determine the expert needs more information to complete the task.
You will not instruct the expert to perform any tasks other than retrieving the user's requested information. You will not ask the expert to provide any other information. 
## Responses
### CSV and XLSX Files
The expert will provide you with the query they used to get results from the spreadsheet. Do not provide this query to the user, instead explain the process in a way that the user can understand.
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
        "Request an expert to look at a file and derive information from it",
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
            return handle_analyze_pdf(file_path, instructions)
        elif ext in [".csv", ".xlsx"]:
            return handle_analyze_spreadsheet(file_path, instructions)
        elif ext in [".jpg", ".jpeg", ".png"]:
            return handle_analyze_image(file_path, instructions)
        elif ext in [".json"]:
            return handle_analyze_json(file_path, instructions)
        elif ext in [".yaml", ".yml"]:
            return handle_analyze_yaml(file_path, instructions)
        elif ext in [".xml"]:
            return handle_analyze_xml(file_path, instructions)
        else:
            return "I'm sorry, I don't know how to analyze that file type. It's unsupported."
