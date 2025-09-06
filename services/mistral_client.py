from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv
from prompts import prompt_model_map

load_dotenv()

api_key = os.getenv('MISTRAL_API_KEY')

if not api_key:
    raise ValueError("MISTRAL_API_KEY not set")

client = MistralClient(api_key=api_key)

def ask_mistral(transcription, model="mistral-large-latest"):
    try:
        messages = [ChatMessage(role="user", content=prompt_model_map[model](transcription))]
        chat_response = client.chat(model=model, messages=messages)
        print(chat_response.choices[0].message.content + "\n")
        return chat_response.choices[0].message.content
    except Exception as e:
        print(e)
        raise ValueError(f"Erro ao processar a mensagem: {str(e)}")