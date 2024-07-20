

class BaseAbility:

    def __init__(self):
        """
        Initializes the ability.
        """
    
    def enable(self, args=None):
        """
        Logic to enable and configure the ability.
        
        Args:
            args (list): The arguments to configure the ability
            
        Raises:
            ValueError: If the arguments are invalid
        """
        
        pass
    
    def disable(self):
        """
        Logic to disable the ability.
        """
        
        pass
    
    def get_prompt(self):
        """
        Used to add additional information to the system prompt.
        
        Returns:
            str | None: A new segment to add to the prompt, or None if no segment should be added
        """
        
        return None
        
    def call_action(self, model, action_name, argument_dict):
        """
        Calls an action with the given arguments.
        
        Args:
            model (BaseModel): The model that is calling the action
            action_name (str): The name of the action
            argument_dict (dict): The arguments to pass to the action
            
        Returns:
            Any: The result of the action
        """
        
        return self.action_handlers[action_name](self, model, argument_dict)
