from flows import flow
from flows.base_flow import BaseFlow

@flow("explain")
class ExplanationFlow(BaseFlow):
    def __init__(self, model):
        super().__init__(model)
        
        self.enable_ability_tools()
        
    def get_system_prompt(self):
        return """
You will provide a detailed explanation of a shell command provided to you by the user. Your explanation should be informative and educational, providing context and reasoning for the command and its usage.
"""

    def get_input_prompt(self, provided_input_str):
        return f"Explain this command: {provided_input_str}"