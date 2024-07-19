class BaseAbility:

    def execute(self, argument_json):
        """
        Executes the ability with the given arguments.
        
        Args:
            argument_json (dict): The arguments to pass to the ability
            
        Returns:
            Any: The result of the ability execution
        """
        
        raise NotImplementedError("Subclasses should implement this!")
    
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
    
