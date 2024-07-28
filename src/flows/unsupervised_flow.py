from flows import flow
from flows.base_flow import BaseFlow
from flows.base_tools import end_process_tool, execute_command_tool
from models.base_model import BaseModel

@flow()
class UnsupervisedFlow(BaseFlow):
    def __init__(self, model: BaseModel):
        super().__init__(model)
        
        self.enable_ability_tools()
        
        self.use_tool(execute_command_tool)
        self.use_tool(end_process_tool)
        
    def get_system_prompt(self):
        return """
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