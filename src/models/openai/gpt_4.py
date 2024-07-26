from models import ModelProvider, ModelTag, model
from models.openai.base_gpt import BaseGPT
from utils.shell_utils import print_fancy, get_system_context, \
    format_markdown_for_terminal


@model(
    ModelProvider.OPEN_AI,
    "gpt-4",
    context_size=8_192,
    cost_per_thousand_input_tokens=0.0300,
    vision_capability=True,
    tags=[ModelTag.MOST_INTELLIGENT]
)
class GPT4Model(BaseGPT):
    """
    A class to interact with the GPT-4 model from OpenAI
    """

    def execute_unsupervised(self, query):
        """
        Performs a task without any user intervention
        
        Args:
            query (str): The task to be performed
        """
        
        messages = [
            {
                "role": "system",
                "content": self.expand_system_prompt(""""
You perform a tasks by using the system shell. Commands you execute should be non-interactive and not require user input, and should not be expecting CTRL+C or other signals. do not let any processes run indefinitely.

Stick to the following process:
1. Create a high-level plan that will be followed to accomplish the task from the shell
1.1 Tools should be used instead of manual command execution where possible
2. Iterate over each step in the plan
2.1 Execute the command for the step
2.2 Review the stdout & stderr output of the command
2.2.1 If the output is as expected, continue to the next step
2.2.2 If the output is not as expected, attempt to resolve the issue before moving on to the next step
3. Repeat steps 2.1-2.2 until all steps in the plan are completed
4. End the process

You will give each step a maximum of 5 attempts to complete successfully. If a step fails after 5 attempts, you will cancel the task and inform the user.
If you successfully complete the task, you will inform the user that the task was completed successfully with a summary of what was done.
""")
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
            
            messages.append(response.choices[0].message)
            
            is_finished, is_failure, returned_messages = self.handle_internal_tools(response)
            
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
                "content": self.expand_system_prompt(""""
You perform a tasks by using the system shell. Commands you execute should be non-interactive and not require user input, and should not be expecting CTRL+C or other signals. do not let any processes run indefinitely.

Stick to the following process:
1. Create a high-level plan that will be followed to accomplish the task from the shell
1.1 Tools should be used instead of manual command execution where possible
2. Iterate over each step in the plan
2.1 Execute the command for the step
2.2 Review the stdout & stderr output of the command
2.2.1 If the output is as expected, continue to the next step
2.2.2 If the output is not as expected, attempt to resolve the issue before moving on to the next step
3. Repeat steps 2.1-2.2 until all steps in the plan are completed
4. End the process

You will give each step a maximum of 5 attempts to complete successfully. If a step fails after 5 attempts, you will cancel the task and inform the user.
If you successfully complete the task, you will inform the user that the task was completed successfully with a summary of what was done.

Each command you execute will need to be marked as "dangerous", which is classified as any command that could modify the system or data in any way.
If the user declines any of your commands, you will not execute them and you will either stop the task or follow the user's instructions.
""")
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
            
            messages.append(response.choices[0].message)
            
            is_finished, is_failure, returned_messages = self.handle_internal_tools(response, require_mutation_approval=True)
            
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
                "content": self.expand_system_prompt("""
You will walk the user through a step-by-step process of accomplishing a task through the system shell. Commands you execute should be non-interactive and should not require user input and should not be expecting CTRL+C or other signals; do not let any processes run indefinitely.

The process will be as follows:
1. Create a high-level plan that will be followed to accomplish the task from the shell
- Tools should be used instead of manual command execution where possible
- Your plan should include testing and validation if applicable
1.1 Review the plan with the user
1.1.1 If the user approves, continue to the first step
1.1.2 If the user has questions, answer them and wait for approval to continue
1.1.2.1 If the user suggests changes, make the changes and review the plan again
2. Iterate over each step in the plan
2.1. Provide an explanation for the step along with any necessary context for teaching purposes
2.2. Provide the command to be executed
2.3. Wait for user approval to execute the command
2.3.1. If the user approves, execute the command
2.3.2. If the user has questions, answer them and wait for approval to execute the command
2.4. Review the stdout & stderr output of the command
2.4.1. Provide a summary of the output to the user in an educational manner
2.4.2. If the output is as expected, continue to the next step
2.4.3. If the output is not as expected, attempt to resolve the issue before moving on to the next step
3. Repeat steps 2.1-2.4 until all steps in the plan are completed
4. End the process

The user will only be able to see what you say through the tools that you call, so you should only output information for internal monologue.
""")
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
                    *ability_tools,
                    self.make_tool(
                        "provide_plan",
                        "Provides a plan to the user for accomplishing the task. This will be a numbered list with titles of each step and no other information",
                        {"plan": "string"},
                        ["plan"]
                    ),
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
            
            messages.append(response.choices[0].message)
            
            is_finished, is_failure, returned_messages = self.handle_internal_tools(response)
            
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
                    "content": """
You will provide a detailed explanation of a shell command provided to you by the user. Your explanation should be informative and educational, providing context and reasoning for the command and its usage.
"""
                },
                {
                    "role": "user",
                    "content": f"Explain the command: {command_string}"
                },
            ],
            tools=self.make_ability_action_tools()
        )
        
        format_markdown_for_terminal(response.choices[0].message.content)
