import openai
from models.base_model.py import BaseModel
from config.secure_store import SecureStore

class GPT4OModel(BaseModel):
    def __init__(self):
        secure_store = SecureStore()
        self.api_key = secure_store.get_api_key("gpt4o")
        openai.api_key = self.api_key

    def generate_command(self, query):
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=f"Generate a shell command for the following task: {query}",
            max_tokens=100
        )
        command = response.choices[0].text.strip()
        return command
