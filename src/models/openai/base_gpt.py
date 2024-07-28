import json
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage
import openai
from models.base_model import BaseModel

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
        
    def run_inference(self, messages, tools=None, temperature=0.1, require_tool_usage=False):
        """
        Method to run inference on a list of messages with a list of tools
        
        Args:
            messages (list): List of messages to run inference on
            tools (list): List of tools to use for inference
            temperature (float): The temperature for the model
            require_tool_usage (bool): Whether to require tool usage
        """
        
        attempts = 0
        response = None
        
        while response is None and attempts < 5:
            attempts += 1
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools,
                    temperature=temperature,
                    tool_choice="required" if require_tool_usage and tools is not None and len(tools) > 0 else None
                )
            except openai.InternalServerError as internal_server_error:
                if "The model produced invalid content" in internal_server_error.message:
                    messages.append({
                        "role": "user",
                        "content": "You provided invalid content. Please try again."
                    })
                    pass
                else:
                    raise internal_server_error
        
        if response is None:
            raise Exception("Model failed to respond")
        
        return response
    
    def make_tool(self, tool_name, description, args=None, required=None, json_parameter_schema=None):
        """
        Creates the structure for describing tools to the model.
        
        Args:
            tool_name (str): The name of the tool
            description (str): The description of the tool
            args (list): The arguments for the tool (optional)
            required (list): The required arguments for the tool (optional)
            json_parameter_schema (dict): The JSON schema for the parameters for advanced usage (optional)
            
        Returns:
            dict: The tool definition
        """

        # If a JSON schema is provided, use it instead of building one the simple way
        if json_parameter_schema is not None:
            return {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": description,
                    "parameters": json_parameter_schema
                }
            }
        
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
    
    def get_tool_call(self, tool_name, obj):
        """
        Parses tool call arguments for a given tool
        
        Args:
            tool_name (str): The name of the tool to get calls for
            obj (dict): The object to search for the tool call
            
        Returns:
            list: The call id, arguments and dictionary, or None if the tool call was not found
        """

        if isinstance(obj, ChatCompletion):
            message = obj.choices[0].message
        elif isinstance(obj, ChatCompletionMessage):
            message = obj
        else:
            return None, None, None

        if message.tool_calls is not None:
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                
                # Check if its a string
                try:
                    if isinstance(tool_call.function.arguments, str):
                        args = json.loads(tool_call.function.arguments)
                    elif isinstance(tool_call.function.arguments, dict):
                        args = tool_call.function.arguments
                    else:
                        args = {}
                except json.JSONDecodeError:
                    return None, None, None
                
                if name.endswith(tool_name):
                    return tool_call.id, args, tool_call

        return None, None, None

    def summarize(self, content):
        """
        Summarizes a block of potentially long text into a smaller summary using the lowest cost model available.
        TODO: We should include a tokenizer so we can be specific about context window requirements and chunk if needed.
        
        Args:
            content (str): The content to summarize
            
        Returns:
            str: The summarized content
        """
        
        from models.base_model_factory import ModelFactory
        model = ModelFactory().get_model(lowest_cost=True)
        
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
        
        response = model.run_inference(
            messages=messages,
            temperature=0.0
        )
        
        return response.choices[0].message.content.strip()
