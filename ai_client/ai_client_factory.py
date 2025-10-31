from .ai_clients.mistral_client import MistralClient
from .ai_clients.gemini_client import GeminiClient


class AIClientFactory:
    model_client_map = {
        "mistral-large-latest": MistralClient,
        "gemini-2.5-flash": GeminiClient,
    }

    @staticmethod
    def create_client(model: str, api_key: str):
        try:
            client_class = AIClientFactory.model_client_map[model]
            return client_class(api_key)
        except KeyError:
            raise ValueError(f"Invalid client type: {model}")
