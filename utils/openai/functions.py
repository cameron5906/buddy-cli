import initialize_abilities
from openai import OpenAI
import json
from config.secure_store import SecureStore
from utils.shell_utils import format_markdown_for_terminal, print_fancy, run_command
from utils.user_input import is_approval, is_denial
from abilities import get_ability


def process_chat_response(model, response, tools=[], require_mutation_approval=False):
    """
    Processes an OpenAI ChatML response, executing any tools and returning the results and status.
    
    Args:
        model (BaseModel): The model that called the response
        response (object): The response object from OpenAI
        require_mutation_approval (bool): Whether to require user approval for any mutation commands
        
    Returns:
        tuple: A tuple containing the finished status, failure status, and a list of messages to add to chat context
    """
    
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
                if require_mutation_approval and "dangerous" in tool_args and tool_args["dangerous"]:
                    is_approved = False
                    print_fancy(f"Proposed command: {tool_args['command']}", bold=True, bg="yellow", color="black")
                    
                    while True:
                        print_fancy("OK to execute? (y/n)", italic=True, color="blue")
                        user_approval_input = input("> ")
                        
                        if is_approval(user_approval_input):
                            is_approved = True
                            
                            break
                        
                        elif is_denial(user_approval_input):
                            print_fancy("Please provide reasoning or provide other instructions", italic=True, color="blue")
                            
                            user_feedback = input("> ")
                            
                            returned_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": "execute_command",
                                "content": f"Command execution denied by user with reasoning: {user_feedback}"
                            })
                            break
                    
                    if not is_approved:
                        continue
                
                stdout, stderr = run_command(tool_args['command'])
                
                if len(stdout) > 1000:
                    stdout = summarize(stdout)
                
                if len(stderr) > 1000:
                    stderr = summarize(stderr)
                
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "execute_command",
                    "content": f"Execution complete\n\n### Stdout Summary\n{stdout}\n\n### Stderr Summary\n{stderr}"
                })
                    
            elif tool_name == "end_process":
                is_finished = True
                if not tool_args['success']:
                    is_failure = True
                    
                if tool_args['summary']:
                    format_markdown_for_terminal(tool_args['summary'])
                    
                returned_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "end_process",
                    "content": "Success"
                })
                
            else:
                # Check if there's a _
                if "_" in tool_name:
                    ability_name = tool_name.split("_")[0]
                    tool_name = tool_name.split(ability_name + "_")[1]
                    
                    ability = get_ability(ability_name)
                    
                    if ability is None:
                        returned_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": "No such ability. Please try again with a different tool"
                        })
                        continue
                    
                    print_fancy(f"Using the {ability_name} ability...", italic=True, color="blue")
                    
                    tool_output = ability.call_action(model, tool_name, tool_args)
                    
                    returned_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_output if tool_output else "Success"
                    })
                else:
                    returned_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": "The tool was not recognized"
                    })
                
    if len(returned_messages) == 0:
        returned_messages.append({
            "role": "system",
            "content": "The user will not be able to see your message as it was not output through a tool"
        })
            
    return is_finished, is_failure, returned_messages


def summarize(content):
    """
    Summarizes a block of potentially long text into a smaller summary.
    
    Args:
        content (str): The content to summarize
        
    Returns:
        str: The summarized content
    """
    
    secure_store = SecureStore()
    api_key = secure_store.get_api_key("gpt-4o")
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
