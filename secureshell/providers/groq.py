"""
Groq Provider Implementation.
Uses OpenAI-compatible API for fast inference with Llama, Mixtral, etc.
"""
from secureshell.providers.openai import OpenAI


class Groq(OpenAI):
    """
    Groq API provider (OpenAI-compatible).
    Supports Llama 3, Mixtral, and other models.
    
    Example:
        provider = GroqProvider(
            api_key="gsk_...",
            model="llama-3.1-70b-versatile"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile"
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.groq.com/openai/v1"
        )

    @property
    def provider_name(self) -> str:
        return "groq"
