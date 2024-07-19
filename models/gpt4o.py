from openai import OpenAI
from models.base_model import BaseModel
from models.openai.functions import make_tool_definition, process_chat_response
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy, get_system_context, \
    format_markdown_for_terminal


class GPT4OModel(BaseModel):
    """
    A class to interact with the GPT-4o model from OpenAI
    """

    def __init__(self):
        """
        Initializes the GPT4OModel by loading the API key from the secure store and creating an OpenAI client.
        """
        
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("openai")
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
                "content": BaseModel.unsupervised_flow_instructions
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
    
        while True:
            response = self.client.chat.completions.create(model="gpt-4o",
            messages=messages,
            tools=[
                make_tool_definition(
                    "execute_command",
                    "Execute a command in the shell",
                    {"command": "string"},
                    ["command"]
                ),
                make_tool_definition(
                    "end_process",
                    "Ends the task, returning control of the terminal to the user",
                    {"success": "boolean", "summary": "string"},
                    ["success", "summary"]
                )
            ],
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False)
            
            is_finished, is_failure, returned_messages = process_chat_response(response)
            
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
                "content": BaseModel.careful_flow_instructions
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
    
        while True:
            response = self.client.chat.completions.create(model="gpt-4o",
            messages=messages,
            tools=[
                make_tool_definition(
                    "execute_command",
                    "Execute a command in the shell",
                    {"command": "string", "dangerous": "boolean"},
                    ["command", "dangerous"]
                ),
                make_tool_definition(
                    "end_process",
                    "Ends the task, returning control of the terminal to the user",
                    {"success": "boolean", "summary": "string"},
                    ["success", "summary"]
                )
            ],
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False)
            
            is_finished, is_failure, returned_messages = process_chat_response(response, require_mutation_approval=True)
            
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
                "content": BaseModel.help_flow_instructions
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
        while True:
            response = self.client.chat.completions.create(model="gpt-4o",
            messages=messages,
            tools=[
                make_tool_definition(
                    "provide_plan",
                    "Provides a plan to the user for accomplishing the task. This will be a numbered list with titles of each step and no other information",
                    {"plan": "string"},
                    ["plan"]
                ),
                make_tool_definition(
                    "provide_explanation",
                    "Provides an explanation for a step to the user in an informative manner. Commands should be explained in a way that can be educational for the user. The title should be the step number or name",
                    {"title": "string", "explanation": "string"},
                    ["explanation"]
                ),
                make_tool_definition(
                    "provide_resolution",
                    "Used to provide the resolution you will attempt after handling an unexpected output from a step. If the issue is not recoverable, the process will end",
                    {"resolution": "string", "recoverable": "boolean"},
                    ["resolution"]
                ),
                make_tool_definition(
                    "provide_command",
                    "Provides a command to be executed as part of a step, prior to execution, for the user to either ask questions about or approve for execution",
                    {"command": "string", "require_sudo": "boolean"},
                    ["command", "require_sudo"]
                ),
                make_tool_definition(
                    "execute_command",
                    "Execute the provided command once approved by the user",
                    {"command": "string"},
                    ["command"]
                ),
                make_tool_definition(
                    "end_process",
                    "Ends the process of providing help to the user",
                    {"success": "boolean"},
                    ["success"]
                )
            ],
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False)
            
            is_finished, is_failure, returned_messages = process_chat_response(response)
            
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
        
        response = self.client.chat.completions.create(model="gpt-4o",
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
        temperature=0.3)
        
        format_markdown_for_terminal(response.choices[0].message.content)
