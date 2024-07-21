from abilities.browsing.utils import get_driver, is_scrolled_to_bottom, scroll_page
from models.base_model_factory import ModelFactory
from utils.shell_utils import print_fancy


def handle_view_webpage(args):
    """
    Allows Buddy to view a webpage using a web browser with vision capabilities.
    Buddy is provided with the following tools:
        stop_reading: Allows Buddy to stop reading the webpage when the instructions have been fulfilled
        add_note: Allows Buddy to add a note to the findings
    
    Args:
        args (dict): The arguments for the search from the model
            url (str): The URL of the webpage to view
            instructions (str): The instructions for what to do on the page
            
    Returns:
        str: An explanation of the findings
    """
    
    model = ModelFactory().get_model(require_vision=True)
    
    url = args["url"]
    instructions = args["instructions"]
    messages = [
        {
            "role": "system",
            "content": f"""
You are viewing a webpage to look for information. You will be provided with instructions on what to do on the webpage.

Obey the following guidelines:
- Provide supporting information back to the user by using the add_note tool
- Upon fulfilling the instructions, stop reading the webpage using the stop_reading tool
- Your notes should be formatted as markdown text
"""
        },
        {
            "role": "user",
            "content": instructions
        }
    ]
    tools = [
        model.make_tool(
            "stop_reading",
            "Stop reading the webpage when you have found the information you need",
            {},
            []
        ),
        model.make_tool(
            "add_note",
            "Add a note to your findings",
            {"note": "string"},
            ["note"]
        )
    ]
    
    driver = get_driver()
    
    print_fancy(f"Opening webpage {url}: {instructions}", italic=True, color="cyan")
    
    driver.get(url)
    
    result_segments = []
    first_look = True
    
    while first_look or not is_scrolled_to_bottom(driver):
        first_look = False
        screen_base64 = driver.get_screenshot_as_base64()
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
        
        response = model.run_inference(
            messages=messages,
            tools=tools
        )
        
        messages.append(response.choices[0].message)
        
        note_call_id, note_call_args, note_call = model.get_tool_call("add_note", response)
        
        if note_call_id is not None:
            result_segments.append(note_call_args["note"])
            messages.append(model.make_tool_result(note_call, "Success"))
            
        if model.get_tool_call("stop_reading", response)[0] is not None:
            break
            
        if not is_scrolled_to_bottom(driver):
            print_fancy("Scrolling for more information...", italic=True, color="cyan")
            scroll_page(driver)
        
    driver.close()
    
    print_fancy("Finished reading the webpage", italic=True, color="cyan")
    
    if len(result_segments) == 0:
        return "No information found"
    
    return "\\n\\n".join(result_segments)
