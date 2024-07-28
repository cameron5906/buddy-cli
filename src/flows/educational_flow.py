from flows import flow
from flows.base_flow import BaseFlow
from flows.base_tools import end_process_tool, execute_command_tool, provide_command_tool, provide_explanation_tool, provide_plan_tool, provide_resolution_tool
from models.base_model import BaseModel

@flow(["help", "teach me", "show me"])
class EducationalFlow(BaseFlow):
    def __init__(self, model: BaseModel):
        super().__init__(model)
        
        self.enable_ability_tools()
        
        self.use_tool(provide_plan_tool)
        self.use_tool(provide_explanation_tool)
        self.use_tool(provide_resolution_tool)
        self.use_tool(provide_command_tool)
        self.use_tool(execute_command_tool)
        self.use_tool(end_process_tool)
        
    def get_system_prompt(self):
        return """
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