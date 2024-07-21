from models.base_model_factory import ModelFactory
from utils.shell_utils import print_fancy
from selenium.webdriver.common.by import By
from abilities.browsing.utils import get_driver, is_scrolled_to_bottom, scroll_page


def handle_perform_google_search(args):
    """
    Allows Buddy to perform a Google search using a web browser with vision capabilities.
    Buddy is provided with the following tools:
        get_link_url: Retrieves the URL by using the title of the search result
    
    Args:
        args (dict): The arguments for the search from the model
            query (str): The search query
            instructions (str): The instructions for the search
            
    Returns:
        str | None: The URL of the first search result, or None if no matching results were found
    """
    
    model = ModelFactory().get_model(require_vision=True)
    
    instructions = args["instructions"]
    query = args["query"]
    
    search_url = f"https://www.google.com/search?q={query}"
    messages = [
        {
            "role": "system",
            "content": f"""
You are performing a Google search based on the instructions provided to you by the user. You will locate the first result that best matches these instructions and provide the URL back to the user.
You will use your vision capabilities to view the results from the Google search page.
You will be able to scroll down the page in order to find the best result.
When you have found a result that you believe matches the goal of the search, you will use your get_link_url tool to retrieve the URL for that result, which will then be returned to the user.
"""
        },
        {
            "role": "user",
            "content": instructions
        }
    ]
    tools = [
        model.make_tool(
            "get_link_url",
            "Retrieves the URL by using the title of the search result",
            {"link_text": "string"},
            ["link_text"]
        )
    ]
    
    driver = get_driver()
    
    print_fancy(f"Performing Google search for '{query}': {instructions}", italic=True, color="cyan")
    
    driver.get(search_url)
    
    print_fancy("Checking results...", italic=True, color="cyan")
    
    result = None
    
    # Keep scrolling and providing screenshots until a result is found or we've hit the end of the page
    while result is None and not is_scrolled_to_bottom(driver):
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
        
        call_id, call_args, call = model.get_tool_call("get_link_url", response)
        
        if call_id is not None:
            link_text = call_args["link_text"]
            link = driver.find_element(By.PARTIAL_LINK_TEXT, link_text)
            
            # If its not an anchor, find the closest one
            if link.tag_name != "a":
                link = link.find_element_by_tag_name("a")
                
            result = link.get_attribute("href")
            
            messages.append(model.make_tool_result(call, result))
            break
            
        scroll_page(driver)
    
    driver.quit()
    
    if result is None:
        return "No results found"
    
    return result
