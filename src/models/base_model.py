import sys
from abilities import get_ability
from config.secure_store import SecureStore
from config.config_manager import ConfigManager
from utils.shell_utils import format_markdown_for_terminal, print_fancy, run_command
from utils.user_input import is_approval, is_denial


class BaseModel:

    model_name = None
    api_key = None
    ability_actions = []
    ability_prompts = {}
    require_supervision = False
    is_executing_ability = False
    
    def __init__(self):
        """
        Initializes the model by loading the API key from the secure store.
        """
        
        self.model_name = getattr(self.__class__, 'model_name', None)
        self.__load_key()    
        self.__load_abilities()
            
    def __load_key(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key(self.provider.value)
        
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
    
    def enhance_system_prompt(self, base_prompt):
        """
        Expands the provided system with extra ability information, if available.
        """
        
        # Get all of the ability_prompts and append them
        ability_prompts = list(self.ability_prompts.values())
        
        if len(ability_prompts) > 0:
            prompt_str = "\\n".join(ability_prompts)
            return f"{base_prompt}\\n\\n{prompt_str}"
        
        return base_prompt
    
    def run_inference(self, messages, tools=None, temperature=0.0, require_tool_usage=False):
        """
        Runs inference on the messages and tools provided.
        
        Args:
            messages (list): The messages to process
            tools (list): The tools to process
            temperature (float): The temperature to use for the model
            require_tool_usage (bool): Whether to require tool usage
            
        Returns:
            tuple: A tuple containing a boolean indicating if the process is finished, a boolean indicating if the process failed, and a list of messages to return
        """
        
        raise NotImplementedError("Subclasses should implement this method")
    
    def make_tool(self, tool_name, description, args=None, required=None, json_parameter_schema=None):
        """
        Creates the structure for describing tools to the model.
        
        Args:
            tool_name (str): The name of the tool
            description (str): The description of the tool
            args (list): The arguments for the tool (optional)
            required (list): The required arguments for the tool (optional)
            json_parameter_schema (dict): The JSON schema for the tool parameters for advanced usage (optional)
            
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
    
    def get_tool_call(self, tool_name, completion_obj):
        """
        Gets the calls for a tool by name.
        
        Args:
            tool_name (str): The name of the tool
            completion_obj (dict): The model completion object to check for the tool call
            
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

    def make_ability_action_tools(self):
        """
        Method to create tools for the ability actions that are available to the model
        """
        
        tools = []
        
        for action in self.ability_actions:
            # Ability_actions store the name as {ability_name}_{action_name}, so we need to substring to get the actual action name
            ability_name = action["name"].split("_")[0]
            action_name = action["name"][len(ability_name) + 1:]
            
            tools.append(
                self.make_tool(
                    action_name,
                    action["description"],
                    action["argument_schema"],
                    action["required_arguments"]
                )
            )
            
        return tools

    def handle_internal_tools(self, response, require_mutation_approval=False):
        """
        Handles built-in tools for regular Buddy flows.
        TODO: Might want to split this out in a later refactor
        
        Args:
            model (BaseModel): The model that the response is from
            response (dict): The response from the model
            require_mutation_approval (bool): Whether to require user approval for any commands that can change the system
            
        Returns:
            is_finished (bool): Whether the process is finished
            is_failure (bool): Whether the process is a failure
            list: A list of messages to add to the chat context
        """
        
        message = response.choices[0].message
        
        if message.tool_calls is None or len(message.tool_calls) == 0:
            return False, None, []
        
        is_finished = False
        is_failure = None  # Can't have a failure if we're not finished
        returned_messages = []
        
        # Handle provide_plan
        provide_plan_id, provide_plan_args, provide_plan_call = self.get_tool_call("provide_plan", message)
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
        provide_explanation_id, provide_explanation_args, provide_explanation_call = self.get_tool_call("provide_explanation", message)
        if provide_explanation_id is not None:
            format_markdown_for_terminal(f"### {provide_explanation_args['title']}\n{provide_explanation_args['explanation']}")
            returned_messages.append(self.make_tool_result(provide_explanation_call, "Success"))

        provide_resolution_id, provide_resolution_args, provide_resolution_call = self.get_tool_call("provide_resolution", message)
        if provide_resolution_id is not None:
            format_markdown_for_terminal(provide_resolution_args['resolution'])
            
            if not provide_resolution_args['recoverable']:
                is_failure = True
                is_finished = True
                
            returned_messages.append(self.make_tool_result(provide_resolution_call, "Success"))
           
        # Handle provide_command 
        provide_command_id, provide_command_args, provide_command_call = self.get_tool_call("provide_command", message)
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
        execute_command_id, execute_command_args, execute_command_call = self.get_tool_call("execute_command", message)
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
                stdout, stderr = run_command(execute_command_args['command'], display_output=not self.is_executing_ability)
                
                if len(stdout) > 1000:
                    stdout = self.summarize(stdout)
                
                if len(stderr) > 1000:
                    stderr = self.summarize(stderr)
                    
                returned_messages.append(self.make_tool_result(execute_command_call, f"Execution complete\n\n### Stdout Summary\n{stdout}\n\n### Stderr Summary\n{stderr}"))
               
        # Handle end_process 
        end_process_id, end_process_args, end_process_call = self.get_tool_call("end_process", message)
        if end_process_id is not None:
            is_finished = True
            if not end_process_args['success']:
                is_failure = True
                
            if "summary" in end_process_args and "details" in end_process_args:
                format_markdown_for_terminal(f"### Summary\n{end_process_args['summary']}\n\n### Details\n{end_process_args['details']}")
            elif "summary" in end_process_args:
                format_markdown_for_terminal(end_process_args['summary'])
            elif "details" in end_process_args:
                format_markdown_for_terminal(end_process_args['details'])
            
            returned_messages.append(self.make_tool_result(end_process_call, "Success"))
            
        # Handle ability actions, loop through the names of the dict
        for ability_action_name in [action["name"] for action in self.ability_actions]:
            ability_name = ability_action_name.split("_")[0]
            action_tool_name = ability_action_name[len(ability_name) + 1:]
            
            ability_action_call_id, ability_action_args, ability_action_call = self.get_tool_call(action_tool_name, message)
            if ability_action_call_id is not None:
                ability = get_ability(ability_name)
                
                if ability is None:
                    returned_messages.append({
                        "role": "tool",
                        "tool_call_id": ability_action_call_id,
                        "name": action_tool_name,
                        "content": "No such ability. Please try again with a different tool"
                    })
                    continue
                
                print_fancy(f"Using the {ability_name} ability...", italic=True, color="blue")
                
                self.is_executing_ability = True
                tool_output = ability.call_action(action_tool_name, ability_action_args)
                self.is_executing_ability = False
                
                returned_messages.append(self.make_tool_result(ability_action_call, tool_output if tool_output else "Success"))

        # Check for unhandled tools and generate error responses
        unhandled_calls = self.get_unhandled_tool_calls(message, returned_messages)
        for unhandled_call in unhandled_calls:
            returned_messages.append({
                "role": "tool",
                "tool_call_id": unhandled_call.id,
                "name": unhandled_call.function.name,
                "content": f"No such tool '{unhandled_call.function.name}'"
            })

        return is_finished, is_failure, returned_messages

    def get_unhandled_tool_calls(self, message, returned_messages):
        """
        Locates any tool calls that do not have responses associated with them

        Args:
            message (dict): The message to check for tool calls
            returned_messages (list): The messages that will be returned
        """
        
        unhandled_calls = []
        
        for tool_call in message.tool_calls:
            if tool_call.id not in [msg["tool_call_id"] for msg in returned_messages]:
                unhandled_calls.append(tool_call)
                print_fancy(f"Unhandled tool call: {tool_call.id} ({tool_call.function.name})", bold=True, color="red")
                
        return unhandled_calls