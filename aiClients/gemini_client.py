from prompts import prompt_model_map
from .ai_client import AIClient
from google import genai


class GeminiClient(AIClient):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def ask_correction(self, transcription, model):
        response = self.client.models.generate_content(
            model=model,
            contents=prompt_model_map[model](transcription),
        )
        return response.text
