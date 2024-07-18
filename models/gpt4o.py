from openai import OpenAI

from models.base_model import BaseModel
from config.secure_store import SecureStore

class GPT4OModel(BaseModel):
    def __init__(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("gpt4o")
        self.client = OpenAI(api_key=self.api_key)

    def generate_command(self, query):
        response = self.client.chat.completions.create(model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You will create shell commands for user requests that will be correctly formatted to be run directly in a system shell. You will not write any other commentary, suggestions, or notes - only the command to run"
            },
            {
                "role": "user",
                "content": query
            }
        ],
        max_tokens=100)
        command = response.choices[0].message.content.strip()
        return command
