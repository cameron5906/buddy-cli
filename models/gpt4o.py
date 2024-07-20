import json
from openai import OpenAI
from models import model
from base_model import BaseModel
from utils.openai.functions import process_chat_response
from utils.shell_utils import print_fancy, get_system_context, \
    format_markdown_for_terminal


@model("gpt-4o")
class GPT4OModel(BaseModel):
    """
    A class to interact with the GPT-4o model from OpenAI
    """

    def __init__(self):
        """
        Initializes the GPT4OModel by creating an OpenAI client instance.
        """
        
        super().__init__()
        self.client = OpenAI(api_key=self.api_key)

    def execute_unsupervised(self, query):
        """
        Performs a task without any user intervention
        
        Args:
            query (str): The task to be performed
        """
        
        messages = [
            {
                "role": "system",
                "content": self.expand_system_prompt(BaseModel.unsupervised_flow_instructions)
            },
            {
                "role": "user",
                "content": f"My system information is:\n{get_system_context()}"  
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        ability_tools = self.make_ability_action_tools()
        
        while True:
            response = self.run_inference(
                messages=messages,
                tools=[
                    *ability_tools,
                    self.make_tool(
                        "execute_command",
                        "Execute a command in the shell",
                        {"command": "string"},
                        ["command"]
                    ),
                    self.make_tool(
                        "end_process",
                        "Ends the task, returning control of the terminal to the user",
                        {"success": "boolean", "summary": "string"},
                        ["success", "summary"]
                    )
                ]
            )
            
            is_finished, is_failure, returned_messages = process_chat_response(self, response, tools=ability_tools)
            
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                
                break
            
            messages = messages + returned_messages
            
        print_fancy("Task completed", bold=True, underline=True, color="green")
    
    def execute_carefully(self, query):
        """
        Perform a task with user intervention for commands that can mutate the system
        
        Args:
            query (str): The task to be performed
        """
        
        messages = [
            {
                "role": "system",
                "content": self.expand_system_prompt(BaseModel.careful_flow_instructions)
            },
            {
                "role": "user",
                "content": f"My system information is:\n{get_system_context()}"  
            },
            {
                "role": "user",
                "content": query
            }
        ]
    
        ability_tools = self.make_ability_action_tools()
    
        while True:
            response = self.run_inference(
                messages=messages,
                tools=[
                    *ability_tools,
                    self.make_tool(
                        "execute_command",
                        "Execute a command in the shell",
                        {"command": "string", "dangerous": "boolean"},
                        ["command", "dangerous"]
                    ),
                    self.make_tool(
                        "end_process",
                        "Ends the task, returning control of the terminal to the user",
                        {"success": "boolean", "summary": "string"},
                        ["success", "summary"]
                    )
                ]
            )
            
            is_finished, is_failure, returned_messages = process_chat_response(self, response, tools=ability_tools, require_mutation_approval=True)
            
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                
                break
            
            messages = messages + returned_messages
            
        print_fancy("Task completed", bold=True, underline=True, color="green")

    def execute_educational(self, query):
        """
        Perform a task while providing helpful context and explanations to the user
        
        Args:
            query (str): The task for which help is required
        """
        
        # Initial messages to start the conversation: system instructions, system information, and user task
        messages = [
            {
                "role": "system",
                "content": self.expand_system_prompt(BaseModel.help_flow_instructions)
            },
            {
                "role": "user",
                "content": f"My system information is:\n{get_system_context()}"  
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # TODO: Add a break condition for infinite loops
        
        ability_tools = self.make_ability_action_tools()
        
        while True:
            response = self.run_inference(
                messages=messages,
                tools=[
                    self.make_tool(
                        "provide_plan",
                        "Provides a plan to the user for accomplishing the task. This will be a numbered list with titles of each step and no other information",
                        {"plan": "string"},
                        ["plan"]
                    ),
                    *ability_tools,
                    self.make_tool(
                        "provide_explanation",
                        "Provides an explanation for a step to the user in an informative manner. Commands should be explained in a way that can be educational for the user. The title should be the step number or name",
                        {"title": "string", "explanation": "string"},
                        ["explanation"]
                    ),
                    self.make_tool(
                        "provide_resolution",
                        "Used to provide the resolution you will attempt after handling an unexpected output from a step. If the issue is not recoverable, the process will end",
                        {"resolution": "string", "recoverable": "boolean"},
                        ["resolution"]
                    ),
                    self.make_tool(
                        "provide_command",
                        "Provides a command to be executed as part of a step, prior to execution, for the user to either ask questions about or approve for execution",
                        {"command": "string", "require_sudo": "boolean"},
                        ["command", "require_sudo"]
                    ),
                    self.make_tool(
                        "execute_command",
                        "Execute the provided command once approved by the user",
                        {"command": "string"},
                        ["command"]
                    ),
                    self.make_tool(
                        "end_process",
                        "Ends the process of providing help to the user",
                        {"success": "boolean"},
                        ["success"]
                    ),
                ]
            )
            
            is_finished, is_failure, returned_messages = process_chat_response(self, response, tools=ability_tools)
            
            # If we're finished, we can break out of the loop
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                
                break
            
            messages = messages + returned_messages
            
        # End of the process
        print_fancy("Task completed", bold=True, underline=True, color="green")

    def explain(self, command_string):
        """
        Generates a detailed explanation of a command for educational purposes.
        
        Args:
            command_string (str): The command to explain
            
        Returns:
            str: The explanation of the command
        """
        
        response = self.run_inference(
            messages=[
                {
                    "role": "system",
                    "content": BaseModel.explain_flow_instructions  
                },
                {
                    "role": "user",
                    "content": f"Explain the command: {command_string}"
                },
            ],
            tools=self.make_ability_action_tools()
        )
        
        format_markdown_for_terminal(response.choices[0].message.content)

    def run_inference(self, messages, tools):
        """
        Method to run inference on a list of messages with a list of tools
        
        Args:
            messages (list): List of messages to run inference on
            tools (list): List of tools to use for inference
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False
        )
        
        return response
    
    def make_tool(self, tool_name, description, args={}, required=[]):
        """
        Creates the structure for describing tools to the model.
        
        Args:
            tool_name (str): The name of the tool
            description (str): The description of the tool
            args (list): The arguments for the tool (optional)
            required (list): The required arguments for the tool (optional)
            
        Returns:
            dict: The tool definition
        """
        
        if args is None:
            args = {"type": "object", "properties": {}}
        if required is None:
            required = []

        properties = {}
        for param, details in args.items():
            if isinstance(details, dict):
                properties[param] = details
            else:
                properties[param] = {"type": details}
                if param in required:
                    properties[param]["description"] = f"{param} is required"

        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
    def make_tool_result(self, tool_call, result):
        """
        Creates the structure for describing tool results to the model.
        
        Args:
            tool_call (str): The tool call dictionary
            result (Any): The result of the tool call
            
        Returns:
            dict: The tool result
        """
        
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": result
        }
    
    def get_tool_call(self, tool_name, response):
        """
        Parses tool call arguments for a given tool
        
        Args:
            tool_name (str): The name of the tool to get calls for
            response (dict): The response from the model
            
        Returns:
            list: The call id, arguments and dictionary, or None if the tool call was not found
        """

        choice = response.choices[0]
        
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if name == tool_name:
                    return tool_call.id, args, tool_call

        return None, None, None

    def make_ability_action_tools(self):
        """
        Method to create tools for the ability actions that are available to the model
        """
        
        tools = []
        
        for action in self.ability_actions:
            tools.append(
                self.make_tool(
                    action["name"],
                    action["description"],
                    action["argument_schema"],
                    action["required_arguments"]
                )
            )
            
        return tools
