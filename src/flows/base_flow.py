import json
from typing import Callable
from models.base_model import BaseModel
from utils.shell_utils import get_system_context, print_fancy


class BaseFlow:
    model: BaseModel
    __tools = []
    
    def __init__(self, model: BaseModel):
        self.model = model
        
    def get_system_prompt(self):
        raise NotImplementedError("This method must be implemented by the derived class")
    
    def get_input_prompt(self, provided_input_str):
        return provided_input_str
    
    def execute(self, input_str):
        system_prompt = self.get_system_prompt()
        user_environment_context = get_system_context()
        user_input = self.get_input_prompt(input_str)
        
        messages = [
            {
                "role": "system",
                "content": self.model.enhance_system_prompt(system_prompt)
            },
            {
                "role": "user",
                "content": f"My system information: {user_environment_context}"
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        
        while True:
            response = self.model.run_inference(
                messages=messages,
                tools=self.__tools,
                require_tool_usage=True
            )
            
            messages.append(response.choices[0].message)
            
            is_finished, is_failure, returned_messages = self.model.handle_internal_tools(response, require_mutation_approval=self.model.require_supervision)
            
            if is_finished:
                if is_failure:
                    print_fancy("Task failed", bold=True, underline=True, color="red")
                    
                break
            
            messages.extend(returned_messages)
            
        # End of the process
        print_fancy("Task completed", bold=True, underline=True, color="green")
    
    def use_tool(self, tool_func: Callable[[BaseModel], None], *args, **kwargs):
        self.__tools.append(tool_func(self.model, *args, **kwargs))
        
    def enable_ability_tools(self):
        for tool in self.model.make_ability_action_tools():
            self.__tools.append(tool)