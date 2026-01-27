"""
DeepSeek Provider Implementation.
Uses OpenAI-compatible API.
"""
from secureshell.providers.openai import OpenAI


class DeepSeek(OpenAI):
    """
    DeepSeek API provider (OpenAI-compatible).
    
    Example:
        provider = DeepSeekProvider(
            api_key="sk-...",
            model="deepseek-chat"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat"
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.deepseek.com/v1"
        )

    @property
    def provider_name(self) -> str:
        return "deepseek"
