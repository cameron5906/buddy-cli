from models import ModelProvider, ModelTag, model
from models.openai.base_gpt import BaseGPT

@model(
    ModelProvider.OPEN_AI,
    "gpt-4",
    context_size=8_192,
    cost_per_thousand_input_tokens=0.0300,
    vision_capability=True,
    tags=[ModelTag.MOST_INTELLIGENT]
)
class GPT4Model(BaseGPT):
    pass