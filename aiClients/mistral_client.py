from mistralai import Mistral
from prompts import prompt_model_map
from .ai_client import AIClient
from flask import abort
from mistralai import models


class MistralClient(AIClient):
    def __init__(self, api_key):
        self.client = Mistral(api_key)

    def ask_correction(self, transcription, model):
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt_model_map[model](transcription),
                },
            ]

            chat_response = self.client.chat.complete(
                model=model,
                messages=messages,
            )
            return chat_response.choices[0].message.content
        except models.HTTPValidationError as e:
            abort(422)
        except models.SDKError as e:
            abort(e.status_code)
