from models import ModelProvider, ModelTag, model
from models.openai.base_gpt import BaseGPT

@model(
    ModelProvider.OPEN_AI,
    "gpt-4o-mini",
    context_size=128_000,
    cost_per_thousand_input_tokens=0.000150,
    vision_capability=True,
    tags=[ModelTag.FASTEST]
)
class GPT4OMiniModel(BaseGPT):
    pass