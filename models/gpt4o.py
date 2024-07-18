import os
import json
from openai import OpenAI
from models.base_model import BaseModel
from utils.shell_utils import run_command, print_fancy
from config.secure_store import SecureStore
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


class GPT4OModel(BaseModel):

    def __init__(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("gpt4o")
        self.client = OpenAI(api_key=self.api_key)
        self.console = Console()

    def generate_command(self, query):
        response = self.client.chat.completions.create(model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You will create shell commands for user requests that will be correctly formatted to be run directly in a system shell. You will not write any other commentary, suggestions, or notes - only the command to run"
            },
            {
                "role": "user",
                "content": query
            }
        ],
        max_tokens=100)
        command = response.choices[0].message.content.strip()
        return command

    def generate_help(self, query):
        messages = [
            {
                "role": "system",
                "content": BaseModel.instructions
            },
            {
                "role": "user",
                "content": query
            }
        ]

        while True:
            response = self.client.chat.completions.create(model="gpt-4o",
            messages=messages,
            tools=[
                self.__makeFunctionTool(
                    "provide_plan",
                    "Provides a plan to the user for accomplishing the task",
                    {"plan": "string"},
                    ["plan"]
                ),
                self.__makeFunctionTool(
                    "provide_explanation",
                    "Provides an explanation for a step to the user in an informative manner",
                    {"explanation": "string"},
                    ["explanation"]
                ),
                self.__makeFunctionTool(
                    "provide_command",
                    "Provides a command to be executed as part of a step, prior to execution, for the user to either ask questions about or approve for execution",
                    {"command": "string", "require_sudo": "boolean"},
                    ["command", "require_sudo"]
                ),
                self.__makeFunctionTool(
                    "execute_command",
                    "Executed the provided command once approved by the user",
                    {"command": "string"},
                    ["command"]
                ),
                self.__makeFunctionTool(
                    "end_process",
                    "Ends the process of providing help to the user",
                    {"success": "boolean"},
                    ["success"]
                )
            ],
            max_tokens=4000,
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False)
            
            is_finished, is_failure, returned_messages = self.__process_response(response)
            
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                
                break
            
            messages = messages + returned_messages
            
        print_fancy("Task completed", bold=True, underline=True, color="green")
            
    def __process_response(self, response):
        choice = response.choices[0]
        returned_messages = [choice.message]
        
        is_finished = False
        is_failure = None
        
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                if tool_name == "provide_plan":
                    self.format_markdown_for_terminal(tool_args['plan'])
                    
                    print_fancy("Plan approved? (y/n)", bold=True, color="blue")
                    
                    user_response = input("> ")
                    
                    if self.__isPositiveApproval(user_response):
                        content = "The plan was approved by the user"
                    elif self.__isNegativeApproval(user_response):
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
                    self.format_markdown_for_terminal(tool_args['explanation'])
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
                    
                    if self.__isPositiveApproval(user_response):
                        content = "The command was approved by the user"
                    elif self.__isNegativeApproval(user_response):
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

    def format_markdown_for_terminal(self, markdown_text):
        md = Markdown(markdown_text)
        self.console.print(Panel(md, expand=True, border_style="bold blue"))

    def __makeFunctionTool(self, name, description, parameterDict=None, required=None):
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
        
    def __isPositiveApproval(self, response):
        return response.lower() == "y" or response.lower() == "yes"
    
    def __isNegativeApproval(self, response):
        return response.lower() == "n" or response.lower() == "no"
