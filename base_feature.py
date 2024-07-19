class BaseFeature:

    def execute(self, argument_json):
        """
        Executes the feature with the given arguments.
        
        Args:
            argument_json (dict): The arguments to pass to the feature
            
        Returns:
            Any: The result of the feature execution
        """
        
        raise NotImplementedError("Subclasses should implement this!")
    
    def enable(self, args=None):
        """
        Logic to enable and configure the feature.
        
        Args:
            args (list): The arguments to configure the feature
            
        Raises:
            ValueError: If the arguments are invalid
        """
        
        pass
    
    def disable(self):
        """
        Logic to disable the feature.
        """
        
        pass
    
