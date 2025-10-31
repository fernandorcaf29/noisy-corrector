import time
from .prompts import prompt_model_map
from ai_client.ai_client import AIClient
from google import genai
from flask import abort


class GeminiClient(AIClient):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def ask_correction(self, transcription, model, custom_prompt=None):
        min_delay = 0.5
        max_delay = 4
        attempt = 0

        while True:
            try:
                if custom_prompt:
                    prompt_content = f"{custom_prompt}\n\n{transcription}"
                else:
                    prompt_content = prompt_model_map[model](transcription)

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt_content,
                )
                
                time.sleep(min_delay)
                return response.text

            except Exception as e:
                if hasattr(e, 'code') and e.code == 429:
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                    print(f"[429] Too Many Requests. Attempt {attempt+1}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                
                elif hasattr(e, 'code') and e.code == 503:
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                    print(f"[503] Service Unavailable. Attempt {attempt+1}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                
                print(f"Error: {e}")
                abort(e.code if hasattr(e, 'code') else 500)