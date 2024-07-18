import json
from utils.shell_utils import format_markdown_for_terminal, print_fancy, run_command
from utils.user_input import is_approval, is_denial


def make_tool_definition(name, description, parameterDict=None, required=None):
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
                
                print_fancy("Plan approved? (y/n)", bold=True, color="blue")
                
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
                format_markdown_for_terminal(tool_args['explanation'])
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "provide_explanation",
                    "content": "Success"
                })
                
            elif tool_name == "provide_command":
                
                print_fancy(f"Proposed command: {tool_args['command']}", bold=True, bg="yellow", color="black")
                print_fancy("Command approved? (y/n)", italic=True, color="blue")
                
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
                
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "execute_command",
                    "content": f"stdout: {stdout}, stderr: {stderr}"
                })
                    
            elif tool_name == "end_process":
                is_finished = True
                if not tool_args['success']:
                    is_failure = True
                
    if len(returned_messages) == 0:
        returned_messages.append({
            "role": "system",
            "content": "The user will not be able to see your message as it was not output through a tool"
        })
            
    return is_finished, is_failure, returned_messages
