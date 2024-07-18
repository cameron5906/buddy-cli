class BaseModel:
    """
    The base class for all models in the system, defining the interface that all models must implement.
    
    Attributes:
        unsupervised_flow_instructions (str): System prompt for the unsupervised flow
        help_flow_instructions (str): System prompt for the educational help flow
    """
    
    unsupervised_flow_instructions = "You will create shell commands for user requests that will be correctly formatted to be run directly in a system shell. You will not write any other commentary, suggestions, or notes - only the command to run"
    
    help_flow_instructions = """You will walk the user through a step-by-step process of accomplishing a task through the system shell. Commands you execute should be non-interactive and should not require user input.

The process will be as follows:
1. Create a high-level plan that will be followed to accomplish the task from the shell
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
3. Repeat steps 2a-2c until all steps in the plan are completed
4. End the process

The user will only be able to see what you say through the tools that you call, so you should only output information for internal monologue."""

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
