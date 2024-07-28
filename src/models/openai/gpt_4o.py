from models import ModelProvider, model
from models.openai.base_gpt import BaseGPT

@model(
    ModelProvider.OPEN_AI,
    "gpt-4o",
    context_size=128_000,
    cost_per_thousand_input_tokens=0.0050,
    vision_capability=True
)
class GPT4OModel(BaseGPT):
    pass