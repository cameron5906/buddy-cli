from models import ModelProvider, ModelTag, model
from models.openai.base_gpt import BaseGPT


@model(
    ModelProvider.OPEN_AI,
    "gpt-4-turbo",
    context_size=128_000,
    cost_per_thousand_input_tokens=0.0100,
    vision_capability=True,
    tags=[ModelTag.BALANCED]
)
class GPT4TurboModel(BaseGPT):
    pass