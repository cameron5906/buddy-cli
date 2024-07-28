import io
import os
import base64
from models.base_model_factory import ModelFactory
from pypdf import PdfReader
from pdf2image import convert_from_path
from utils.shell_utils import print_fancy


def handle_analyze_pdf(file_path, instructions):
    """
    Analyzes a PDF file based on provided instructions, returning the requested information.
    
    There are two methods of analysis:
    - If a vision capable model is available, the model will be used to read the PDF
    - If no model is found, PyPDF2 will be used to extract text and then a model will be used to analyze the text

    Args:
        file_path (str): The path to the PDF file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
    
    if not file_path.endswith(".pdf"):
        return "Unsupported file extension. Only .pdf files are supported."
    
    if not os.path.exists(file_path):
        return "The file does not exist."
    
    model = ModelFactory().get_model(require_vision=True)
    
    print_fancy(f"Opening PDF file: {file_path}: {instructions}", italic=True, color="cyan")
    
    if model is None:
        return __get_answer_using_extraction(file_path, instructions)
    else:
        return __get_answer_using_vision(model, file_path, instructions)
        

def __get_answer_using_extraction(file_path, instructions):
    """
    Analyzes a PDF file using text extraction and returns the requested information by using a model to analyze the text.
    
    Args:
        file_path (str): The path to the PDF file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
    
    # Initialize the reader
    reader = PdfReader(file_path)
    all_text = ""
    
    print_fancy("Extracting text from the PDF", italic=True, color="cyan")
    
    # Extract text from each page
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        all_text += page.extract_text()
    
    # Get a model to analyze the text
    model = ModelFactory().get_model(require_vision=False, lowest_cost=True)
    messages = [
        {
            "role": "system",
            "content": """
You will extract information from a body of text provided to you by the user. You will be provided with detailed instructions on what information to extract.
You will only extract the information requested and will not provide any additional information.
Instead of providing the exact text, you will provide a summary of the information you found.
"""
        },
        {
            "role": "user",
            "content": all_text
        },
        {
            "role": "user",
            "content": instructions
        }
    ]
    
    print_fancy("Analyzing the text", italic=True, color="cyan")
    
    # Generate the response
    response = model.run_inference(messages=messages, temperature=0.0)
    
    return response.choices[0].message.content.strip()


def __get_answer_using_vision(model, file_path, instructions):
    """
    Analyzes a PDF file using a vision capable model and returns the requested information.
    
    Args:
        model (Model): The vision capable model to use for analysis
        file_path (str): The path to the PDF file
        instructions (str): Detailed instructions for what information to retrieve
        
    Returns:
        str: The analysis results
    """
        
    # Initialize the reader
    reader = PdfReader(file_path)
    
    # Collect pages as images
    images = []
    for page_num in range(len(reader.pages)):
        images.extend(convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1))
    
    # Initialize model variables
    messages = [
        {
            "role": "system",
            "content": f"""
You are reading through pages of a PDF file to look for information for the user. Your goal is to locate the information requested in the instructions.
To not waste time, you will stop reading the PDF using the stop_reading tool when you are confident that you have identified the information requested.
If a page does not contain any relevant content, you will use the skip_page tool to move to the next page.

Requirements:
{instructions}
"""
        }
    ]
    tools = [
        model.make_tool(
            "stop_reading",
            "Stop reading the PDF when you have found the information you need",
            {},
            []
        ),
        model.make_tool(
            "skip_page",
            "Skip the current page and move to the next one",
            {},
            []
        )
    ]
    
    notes = []
    
    # Feed in each page
    for image_index in range(len(images)):
        image = images[image_index]
        
        # Convert PIL image to byte array
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        screen_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screen_base64}"
                    }
                }
            ]
        })
        
        print_fancy(f"Reading page {image_index + 1}", italic=True, color="cyan")
        
        response = model.run_inference(messages=messages, tools=tools)
        
        messages.append(response.choices[0].message)
        
        # Check if we should skip the page
        skip_page_call_id, _, skip_page_call = model.get_tool_call("skip_page", response)
        if skip_page_call_id is not None:
            messages.append(model.make_tool_result(skip_page_call, "Moving to the next page"))
            continue
        
        note = response.choices[0].message.content
        
        # Add output as notes
        if note is not None:
            notes.append(note)
            
        # Check if it's time to stop reading
        stop_reading_call_id, _, stop_reading_call = model.get_tool_call("stop_reading", response)
        if stop_reading_call_id is not None:
            messages.append(model.make_tool_result(stop_reading_call, "Success"))
            break
        
    print_fancy("Finished reading the PDF", italic=True, color="cyan")
    
    if len(notes) == 0:
        return "No information found"
    
    return "\n".join(notes)
