from openai import OpenAI
from models.base_model import BaseModel
from models.openai.functions import make_tool_definition, process_chat_response
from config.secure_store import SecureStore
from utils.shell_utils import print_fancy, get_system_context


class GPT4OModel(BaseModel):

    def __init__(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("openai")
        self.client = OpenAI(api_key=self.api_key)

    def generate_command(self, query):
        response = self.client.chat.completions.create(model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": BaseModel.unsupervised_flow_instructions
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
                    "Executed the provided command once approved by the user",
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
            
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                
                break
            
            messages = messages + returned_messages
            
        print_fancy("Task completed", bold=True, underline=True, color="green")
