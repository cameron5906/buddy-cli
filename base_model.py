import initialize_abilities
import sys
from abilities import get_ability
from config.secure_store import SecureStore
from config.config_manager import ConfigManager
from utils.shell_utils import format_markdown_for_terminal, print_fancy, run_command
from utils.user_input import is_approval, is_denial


class BaseModel:

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
    
    def summarize(self, content):
        """
        Summarizes a block of potentially long text into a smaller summary using the most efficient model available from a given provider.
        
        Args:
            content (str): The content to summarize
            
        Returns:
            str: The summarized content
        """
        
        raise NotImplementedError("Subclasses should implement this method")

    def handle_internal_tools(self, response, require_mutation_approval=False):
        """
        Handles built-in tools for regular Buddy flows.
        
        Args:
            model (BaseModel): The model that the response is from
            response (dict): The response from the model
            require_mutation_approval (bool): Whether to require user approval for any commands that can change the system
            
        Returns:
            is_finished (bool): Whether the process is finished
            is_failure (bool): Whether the process is a failure
            list: A list of messages to add to the chat context
        """
        
        is_finished = False
        is_failure = None  # Can't have a failure if we're not finished
        returned_messages = []
        
        # Handle provide_plan
        provide_plan_id, provide_plan_args, provide_plan_call = self.get_tool_call("provide_plan", response)
        if provide_plan_id is not None:
            format_markdown_for_terminal(provide_plan_args['plan'])
            
            print_fancy("Does this plan look right? (y/n)", bold=True, color="blue")
            
            user_response = input("> ")
            
            if is_approval(user_response):
                content = "The plan was approved by the user"
            elif is_denial(user_response):
                content = "The user did not approve the plan"
            else:
                content = user_response
                
            returned_messages.append(self.make_tool_result(provide_plan_call, content))

        # Handle provide_explanation
        provide_explanation_id, provide_explanation_args, provide_explanation_call = self.get_tool_call("provide_explanation", response)
        if provide_explanation_id is not None:
            format_markdown_for_terminal(f"### {provide_explanation_args['title']}\n{provide_explanation_args['explanation']}")
            returned_messages.append(self.make_tool_result(provide_explanation_call, "Success"))

        provide_resolution_id, provide_resolution_args, provide_resolution_call = self.get_tool_call("provide_resolution", response)
        if provide_resolution_id is not None:
            format_markdown_for_terminal(provide_resolution_args['resolution'])
            
            if not provide_resolution_args['recoverable']:
                is_failure = True
                is_finished = True
                
            returned_messages.append(self.make_tool_result(provide_resolution_call, "Success"))
           
        # Handle provide_command 
        provide_command_id, provide_command_args, provide_command_call = self.get_tool_call("provide_command", response)
        if provide_command_id is not None:
            print_fancy(f"Proposed command: {provide_command_args['command']}", bold=True, bg="yellow", color="black")
            print_fancy("Do you approve? (y/n)", italic=True, color="blue")
            
            user_response = input("> ")
            
            if is_approval(user_response):
                content = "The command was approved by the user"
            elif is_denial(user_response):
                content = "The user did not approve the command"
            else:
                content = user_response
                
            returned_messages.append(self.make_tool_result(provide_command_call, "Success"))
            
        # Handle execute_command
        execute_command_id, execute_command_args, execute_command_call = self.get_tool_call("execute_command", response)
        if execute_command_id is not None:
            if require_mutation_approval and "dangerous" in execute_command_args and execute_command_args["dangerous"]:
                is_approved = False
                print_fancy(f"Proposed command: {execute_command_args['command']}", bold=True, bg="yellow", color="black")
                
                while True:
                    print_fancy("OK to execute? (y/n)", italic=True, color="blue")
                    user_approval_input = input("> ")
                    
                    if is_approval(user_approval_input):
                        is_approved = True
                        
                        break
                    
                    elif is_denial(user_approval_input):
                        print_fancy("Please provide reasoning or provide other instructions", italic=True, color="blue")
                        
                        user_feedback = input("> ")
                        
                        returned_messages.append(self.make_tool_result(execute_command_call, f"Command execution denied by user with reasoning: {user_feedback}"))
                        break
            else:
                is_approved = True
            
            if is_approved or not require_mutation_approval:
                stdout, stderr = run_command(execute_command_args['command'])
                
                if len(stdout) > 1000:
                    stdout = self.summarize(stdout)
                
                if len(stderr) > 1000:
                    stderr = self.summarize(stderr)
                    
                returned_messages.append(self.make_tool_result(execute_command_call, f"Execution complete\n\n### Stdout Summary\n{stdout}\n\n### Stderr Summary\n{stderr}"))
               
        # Handle end_process 
        end_process_id, end_process_args, end_process_call = self.get_tool_call("end_process", response)
        if end_process_id is not None:
            is_finished = True
            if not end_process_args['success']:
                is_failure = True
                
            if end_process_args['summary']:
                format_markdown_for_terminal(end_process_args['summary'])
            
            returned_messages.append(self.make_tool_result(end_process_call, "Success"))
            
        # Handle ability actions
        for ability_action_name in self.ability_actions:
            ability_action_call_id, ability_action_args, ability_action_call = self.get_tool_call(ability_action_name, response)
            if ability_action_call_id is not None:
                ability_name = ability_action_name.split("_")[0]
                tool_name = ability_action_name.split(ability_name + "_")[1]
                
                ability = get_ability(ability_name)
                
                if ability is None:
                    returned_messages.append({
                        "role": "tool",
                        "tool_call_id": ability_action_call_id,
                        "name": tool_name,
                        "content": "No such ability. Please try again with a different tool"
                    })
                    continue
                
                print_fancy(f"Using the {ability_name} ability...", italic=True, color="blue")
                
                tool_output = ability.call_action(self, tool_name, ability_action_args)
                
                returned_messages.append(self.make_tool_result(ability_action_call, tool_output if tool_output else "Success"))

        return is_finished, is_failure, returned_messages
