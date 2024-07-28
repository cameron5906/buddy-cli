import base64
import mimetypes
from models.base_model_factory import ModelFactory
from utils.shell_utils import print_fancy


def handle_analyze_image(file_path, instructions):
    """
    Analyzes an image file based on provided instructions, returning the requested information.
    
    Args:
        file_path (str): The path to the image file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type is None:
        return "The file type could not be determined, I can't process this."
    
    print_fancy(f"Looking at the image {file_path}: {instructions}", italic=True, color="cyan")
    
    with open(file_path, "rb") as f:
        base64_str = base64.b64encode(f.read()).decode("utf-8")
    
        model = ModelFactory().get_model(require_vision=True, lowest_cost=True)
        
        messages = [
            {
                "role": "system",
                "content": """
You will answer the user's query about the provided image. You will avoid telling the user about obeying guidelines or rules and instead focus on answering their question without providing sensitive information.
You will concentrate on general characteristics, themes, and other relevant details.
"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_str}"
                        }
                    }
                ]
            },
            {
                "role": "user",
                "content": instructions
            }
        ]
        
        response = model.run_inference(messages=messages)
        
        return response.choices[0].message.content