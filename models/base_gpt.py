import json
from openai import OpenAI
from base_model import BaseModel
from config.secure_store import SecureStore


class BaseGPT(BaseModel):
    """
    Base for all OpenAI GPT models.
    
    Attributes:
        api_key (str): The OpenAI API key
        client (OpenAI): The OpenAI client instance
        ability_actions (list): The list of ability actions available to the model
    """

    def __init__(self):
        """
        Initializes the GPT4OModel by creating an OpenAI client instance.
        """
        
        super().__init__()
        self.client = OpenAI(api_key=self.api_key)

    def run_inference(self, messages, tools):
        """
        Method to run inference on a list of messages with a list of tools
        
        Args:
            messages (list): List of messages to run inference on
            tools (list): List of tools to use for inference
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
            parallel_tool_calls=False
        )
        
        return response
    
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
        
        if args is None:
            args = {"type": "object", "properties": {}}
        if required is None:
            required = []

        properties = {}
        for param, details in args.items():
            if isinstance(details, dict):
                properties[param] = details
            else:
                properties[param] = {"type": details}
                if param in required:
                    properties[param]["description"] = f"{param} is required"

        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
    def make_tool_result(self, tool_call, result):
        """
        Creates the structure for describing tool results to the model.
        
        Args:
            tool_call (str): The tool call dictionary
            result (Any): The result of the tool call
            
        Returns:
            dict: The tool result
        """
        
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": result
        }
    
    def get_tool_call(self, tool_name, response):
        """
        Parses tool call arguments for a given tool
        
        Args:
            tool_name (str): The name of the tool to get calls for
            response (dict): The response from the model
            
        Returns:
            list: The call id, arguments and dictionary, or None if the tool call was not found
        """

        choice = response.choices[0]
        
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if name == tool_name:
                    return tool_call.id, args, tool_call

        return None, None, None

    def make_ability_action_tools(self):
        """
        Method to create tools for the ability actions that are available to the model
        """
        
        tools = []
        
        for action in self.ability_actions:
            tools.append(
                self.make_tool(
                    action["name"],
                    action["description"],
                    action["argument_schema"],
                    action["required_arguments"]
                )
            )
            
        return tools

    def summarize(self, content):
        """
        Summarizes a block of potentially long text into a smaller summary.
        
        Args:
            content (str): The content to summarize
            
        Returns:
            str: The summarized content
        """
        
        secure_store = SecureStore()
        api_key = secure_store.get_api_key("gpt-4o")
        client = OpenAI(api_key=api_key)
        
        messages = [
            {
                "role": "system",
                "content": "You will condense the user's message into a concise, informative summary that captures meaningful details and context. You will attempt to keep the summary as short as possible while maintaining the necessary information it conveys"
            },
            {
                "role": "user",
                "content": content
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.0)
        
        return response.choices[0].message.content.strip()
