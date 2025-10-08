import time
from mistralai import Mistral
from prompts import prompt_model_map
from .ai_client import AIClient
from flask import abort
from mistralai import models
from services.asr_corrector import ASRCorrector

class MistralClient(AIClient):
    def __init__(self, api_key):
        self.client = Mistral(api_key)
        self.asr_corrector = ASRCorrector(self)

    def ask_correction(self, transcription, model, custom_prompt=None):
        min_delay = 0.2
        max_delay = 1
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            try:
                if model in ["mistral-large-latest"]:
                    content, metadata = self.asr_corrector.preprocess(transcription)
                    
                    if custom_prompt:
                        prompt_content = f"{custom_prompt}\n\nTRANSCRIÇÃO ORIGINAL:\n\n{content}"
                    else:
                        prompt_content = prompt_model_map[model](content)

                    messages = [
                        {
                            "role": "user",
                            "content": prompt_content,
                        }
                    ]

                    chat_response = self.client.chat.complete(
                        model=model,
                        messages=messages,
                        temperature=0.1
                    )

                    corrected_content = chat_response.choices[0].message.content
                    
                    final_text = self.asr_corrector.postprocess(corrected_content, metadata)
                else:
                    if custom_prompt:
                        prompt_content = f"{custom_prompt}\n\n{transcription}"
                    else:
                        prompt_content = prompt_model_map[model](transcription)

                    messages = [
                        {
                            "role": "system",
                            "content":prompt_model_map["header"] 
                        },
                        {
                            "role": "user",
                            "content": prompt_content,

                        },
                    ]

                    chat_response = self.client.chat.complete(
                        model=model,
                        messages=messages,
                        temperature=0.1
                    )

                    raw_response = chat_response.choices[0].message.content
                    final_text = self.asr_corrector.remove_formatting(raw_response)
                
                time.sleep(min_delay)
                return final_text

            except models.HTTPValidationError:
                abort(422)

            except models.SDKError as e:
                if e.status_code == 429:
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                    print(f"[429] Too Many Requests. Attempt {attempt+1}/{max_attempts}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                abort(e.status_code)
      
        raise Exception(f"Failed after {max_attempts} attempts due to rate limiting")
