import initialize_abilities
import sys
from abilities import get_ability
from config.secure_store import SecureStore
from config.config_manager import ConfigManager
from utils.shell_utils import print_fancy


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
