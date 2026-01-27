"""
llama.cpp Provider Implementation.
For running local models via llama.cpp server (OpenAI-compatible endpoint).
"""
from secureshell.providers.openai import OpenAI


class LlamaCpp(OpenAI):
    """
    llama.cpp server provider (OpenAI-compatible).
    Requires llama.cpp server running with --api flag.
    
    Example:
        # Start llama.cpp server:
        # ./server -m model.gguf --api --port 8080
        
        provider = LlamaCppProvider(
            model="local",
            base_url="http://localhost:8080/v1"
        )
    """
    
    def __init__(
        self,
        model: str = "local",
        base_url: str = "http://localhost:8080/v1"
    ):
        # llama.cpp doesn't need API key for local server
        super().__init__(
            api_key="not-needed",
            model=model,
            base_url=base_url
        )

    @property
    def provider_name(self) -> str:
        return "llama_cpp"
