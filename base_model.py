import initialize_abilities
import sys
from abilities import get_ability
from config.secure_store import SecureStore
from config.config_manager import ConfigManager
from utils.shell_utils import print_fancy


class BaseModel:
    """
    The base class for all models in the system, defining the interface that all models must implement.
    
    Attributes:
        unsupervised_flow_instructions (str): System prompt for the unsupervised flow
        help_flow_instructions (str): System prompt for the educational help flow
    """
    
    unsupervised_flow_instructions = """"
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
"""

    careful_flow_instructions = """"
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
"""
    
    help_flow_instructions = """
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
"""

    explain_flow_instructions = """
You will provide a detailed explanation of a shell command provided to you by the user. Your explanation should be informative and educational, providing context and reasoning for the command and its usage.
"""

    def __init__(self):
        """
        Initializes the model by loading the API key from the secure store.
        """
        
        self.model_name = getattr(self.__class__, 'model_name', None)
        self.__load_key()    
        self.__load_abilities()
            
    def __load_key(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key(self.model_name)
        
        if self.api_key is None:
            print_fancy("You haven't provided an API key for this model. See 'buddy info' for more information", bold=True, color="red")
            sys.exit(1)
        
    def __load_abilities(self):
        
        enabled_abilities = ConfigManager().get_abilities()
        
        self.ability_actions = []
        self.ability_prompts = {}
        
        for ability_name in enabled_abilities:
            ability = get_ability(ability_name)
            
            ability_prompt = ability.get_prompt()
            
            if ability_prompt is not None:
                self.ability_prompts[ability_name] = ability_prompt
            
            if ability.actions:
                for action in ability.actions:
                    self.ability_actions.append(action)
            else:
                print_fancy(f"No actions found for {ability_name} ability.", bold=True, color="red")

    def execute_unsupervised(self, query):
        """
        Method for performing unsupervised tasks that don't require any user interaction.
        
        Args:
            query (str): The task to be performed
            
        Raises:
            NotImplementedError: Subclasses should implement this method
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def execute_carefully(self, query):
        """
        Method for performing supervised tasks that require user confirmation before execution of non-read commands.
        
        Args:
            query (str): The task to be performed
            
        Raises:
            NotImplementedError: Subclasses should implement this method
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def execute_educational(self, query):
        """
        Method for walking a user through a task step-by-step while being informative and educational.
        
        Args:
            query (str): The task for which help is required
            
        Raises:
            NotImplementedError: Subclasses should implement this method
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def explain(self, command_string):
        """
        Generates a detailed explanation of a command for educational purposes.
        
        Args:
            command_string (str): The command to explain
            
        Returns:
            str: The explanation of the command
            
        Raises:
            NotImplementedError: Subclasses should implement this method
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def expand_system_prompt(self, base_prompt):
        """
        Expands the provided system with extra ability information, if available.
        """
        
        # Get all of the ability_prompts and append them
        ability_prompts = list(self.ability_prompts.values())
        
        if len(ability_prompts) > 0:
            prompt_str = "\\n".join(ability_prompts)
            return f"{base_prompt}\\n\\n{prompt_str}"
        
        return base_prompt
    
    def run_inference(self, messages, tools):
        """
        Runs inference on the messages and tools provided.
        
        Args:
            messages (list): The messages to process
            tools (list): The tools to process
            
        Returns:
            tuple: A tuple containing a boolean indicating if the process is finished, a boolean indicating if the process failed, and a list of messages to return
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
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
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def make_tool_result(self, tool_call, result):
        """
        Creates the structure for describing tool results to the model.
        
        Args:
            tool_call (str): The tool call dictionary
            result (Any): The result of the tool call
            
        Returns:
            dict: The tool result
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def get_tool_call(self, tool_name, response):
        """
        Gets the calls for a tool by name.
        
        Args:
            tool_name (str): The name of the tool
            response (dict): The response from the model
            
        Returns:
            list: The call id, arguments, and call dictionary
        """
        
        raise NotImplementedError("Subclasses should implement this method")
