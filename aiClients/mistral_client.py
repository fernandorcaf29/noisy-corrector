from mistralai.client import MistralClient as MistralAIClient
from mistralai.models.chat_completion import ChatMessage
from prompts import prompt_model_map
from .ai_client import AIClient


class MistralClient(AIClient):
    def __init__(self, api_key):
        self.client = MistralAIClient(api_key)

    def ask_correction(self, transcription, model):
        try:
            messages = [
                ChatMessage(role="user", content=prompt_model_map[model](transcription))
            ]
            chat_response = self.client.chat(model=model, messages=messages)
            print(chat_response.choices[0].message.content + "\n")
            return chat_response.choices[0].message.content
        except Exception as e:
            print(e)
            raise ValueError(f"Erro ao processar a mensagem: {str(e)}")
