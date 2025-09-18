from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import time
import random
from dotenv import load_dotenv
from prompts import prompt_model_map

load_dotenv()

api_key = os.getenv('MISTRAL_API_KEY')

if not api_key:
    raise ValueError("MISTRAL_API_KEY not set")

client = MistralClient(api_key=api_key)

def ask_mistral(transcription, model="mistral-large-latest", max_retries=3):
    retry_count = 0
    base_delay = 0.2
    
    while retry_count <= max_retries:
        try:
            messages = [ChatMessage(role="user", content=prompt_model_map[model](transcription))]
            chat_response = client.chat(model=model, messages=messages)
            
            response_content = chat_response.choices[0].message.content
            
            if retry_count > 0:
                print(f"Success after {retry_count} retry(s)!")
            
            return response_content
            
        except Exception as e:
            retry_count += 1
            
            if retry_count > max_retries:
                error_msg = f"All the {max_retries} retry(s) have failed. last error: {str(e)}"
                print(error_msg)
                raise ValueError(error_msg)
            
            delay = base_delay * (2 ** (retry_count - 1))
            jitter = random.uniform(0, delay * 0.3)
            actual_delay = delay + jitter
            
            error_type = type(e).__name__
            print(f"Attempt {retry_count}/{max_retries} failed ({error_type})")
            print(f"Retry in {actual_delay:.2f} seconds...")
            
            time.sleep(actual_delay)