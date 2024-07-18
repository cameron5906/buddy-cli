from openai import OpenAI

from models.base_model import BaseModel
from config.secure_store import SecureStore

class GPT4OModel(BaseModel):
    def __init__(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("gpt4o")
        self.client = OpenAI(api_key=self.api_key)


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
        response = self.client.chat.completions.create(model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You will walk the user through a step-by-step process of accomplishing a task through the system shell.
In order to perform your duty, you will utilize the following tools:
- provide_plan: Used to provide the step-by-step plan for a specific task. You will use this as an introductory message for a new task.
- provide_explanation: Used to provide an explanation for a step with reasoning why it must be done.
- provide_command: Used to provide the command that will be executed as part of a step, after the explanation.
- execute_command: Used to execute the approved command against the system shell. Results from stdout and stderr will be provided to you.

You will provide an explanation for each step and provide the command at the same time. Once these are provided, the user will be able to ask questions OR permit you to continue.
Upon executing a command, you will review the stdout & stderr output to determine if you can continue with your plan, or if you need to resolve an issue prior to moving on with the plan."""
            }
        ],
        tools=[
            __makeFunctionTool(
                "provide_plan", 
                "Provides a plan to the user for accomplishing the task", 
                { "plan": "string" }, 
                ["plan"]
            ),
            __makeFunctionTool(
                "provide_explanation", 
                "Provides an explanation for a step to the user in an informative manner", 
                { "explanation": "string" }, 
                ["explanation"]
            ),
            __makeFunctionTool(
                "provide_command", 
                "Provides a command to be executed as part of a step, prior to execution, for the user to either ask questions about or approve for execution", 
                { "command": "string", "require_sudo": "boolean" }, 
                ["command", "require_sudo"]
            ),
            __makeFunctionTool(
                "execute_command",
                "Executed the provided command once approved by the user",
                { "command": "string" },
                ["command"]
            )
        ],
        max_tokens=4000)
        content = response.choices[0].message.content.strip()
        return content

    def __makeFunctionTool(name, description, parameterDict=None, required=None):
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
