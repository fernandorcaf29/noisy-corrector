import time
from mistralai import Mistral
from prompts import prompt_model_map
from .ai_client import AIClient
from flask import abort
from mistralai import models


class MistralClient(AIClient):
    def __init__(self, api_key):
        self.client = Mistral(api_key)

    def ask_correction(self, transcription, model):
        min_delay = 0.2
        max_delay = 30
        attempt = 0

        while True:
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
                    temperature=0.2
                )

                # Pequeno delay após sucesso
                time.sleep(min_delay)
                return chat_response.choices[0].message.content

            except models.HTTPValidationError:
                abort(422)

            except models.SDKError as e:
                if e.status_code == 429:
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                   ## print(f"[429] Too Many Requests. Attempt {attempt+1}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                abort(e.status_code)
