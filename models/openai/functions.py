from openai import OpenAI
import json
from config.secure_store import SecureStore
from utils.shell_utils import format_markdown_for_terminal, print_fancy, run_command
from utils.user_input import is_approval, is_denial


def make_tool_definition(name, description, parameterDict=None, required=None):
    """
    Creates an OpenAI ChatML tool definition object based on provided metadata.
    
    Args:
        name (str): The name of the tool
        description (str): A description of the tool
        parameterDict (dict): A dictionary of parameters for the tool (key: parameter name, value: parameter type)
        required (list): A list of required parameters
        
    Returns:
        dict: The tool definition object
    """
    
    if parameterDict is None:
        parameterDict = {"type": "object", "properties": {}}
    if required is None:
        required = []

    properties = {}
    for param, details in parameterDict.items():
        if isinstance(details, dict):
            properties[param] = details
        else:
            properties[param] = {"type": details}
            if param in required:
                properties[param]["description"] = f"{param} is required"

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


def process_chat_response(response):
    choice = response.choices[0]
    returned_messages = [choice.message]
    
    is_finished = False
    is_failure = None
    
    if choice.finish_reason == "tool_calls":
        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            if tool_name == "provide_plan":
                format_markdown_for_terminal(tool_args['plan'])
                
                print_fancy("Does this plan look right? (y/n)", bold=True, color="blue")
                
                user_response = input("> ")
                
                if is_approval(user_response):
                    content = "The plan was approved by the user"
                elif is_denial(user_response):
                    content = "The user did not approve the plan"
                else:
                    content = user_response
                
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "provide_plan",
                    "content": content
                })
                
            elif tool_name == "provide_explanation":
                format_markdown_for_terminal(f"### {tool_args['title']}\n{tool_args['explanation']}")
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "provide_explanation",
                    "content": "Success"
                })
                
            elif tool_name == "provide_resolution":
                format_markdown_for_terminal(tool_args['resolution'])
                
                if not tool_args['recoverable']:
                    is_failure = True
                    is_finished = True
                    
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "provide_resolution",
                    "content": "Success"
                })
                
            elif tool_name == "provide_command":
                
                print_fancy(f"Proposed command: {tool_args['command']}", bold=True, bg="yellow", color="black")
                print_fancy("Do you approve? (y/n)", italic=True, color="blue")
                
                user_response = input("> ")
                
                if is_approval(user_response):
                    content = "The command was approved by the user"
                elif is_denial(user_response):
                    content = "The user did not approve the command"
                else:
                    content = user_response
                
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "provide_command",
                    "content": content
                })
                
            elif tool_name == "execute_command":
                stdout, stderr = run_command(tool_args['command'])
                
                summarized_out = summarize(stdout)
                summarized_err = summarize(stderr)
                
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "execute_command",
                    "content": f"Execution complete\n\n### Stdout Summary\n{summarized_out}\n\n### Stderr Summary\n{summarized_err}"
                })
                    
            elif tool_name == "end_process":
                is_finished = True
                if not tool_args['success']:
                    is_failure = True
                    
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "end_process",
                    "content": "Success"
                })
                
    if len(returned_messages) == 0:
        returned_messages.append({
            "role": "system",
            "content": "The user will not be able to see your message as it was not output through a tool"
        })
            
    return is_finished, is_failure, returned_messages


def summarize(content):
    secure_store = SecureStore()
    api_key = secure_store.get_api_key("openai")
    client = OpenAI(api_key=api_key)
    
    messages = [
        {
            "role": "system",
            "content": "You will condense the user's message into a concise, informative summary that captures meaningful details and context. You will attempt to keep the summary as short as possible while maintaining the necessary information it conveys"
        },
        {
            "role": "user",
            "content": content
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0)
    
    return response.choices[0].message.content.strip()
