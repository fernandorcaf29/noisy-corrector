import time
from mistralai import Mistral, models
from .ai_client import AIClient
from services.rate_limiter import RateLimiter
from services.metadata.metadata_extractor import MetadataExtractor
from services.metadata.response_parser import ResponseParser
from services.asr_corrector import ASRCorrector
from prompts import prompt_model_map

class MistralRateLimiter(RateLimiter):
    def _is_rate_limit_error(self, error: Exception) -> bool:
        return (hasattr(error, 'status_code') and getattr(error, 'status_code') == 429) or \
               (isinstance(error, models.SDKError) and getattr(error, 'status_code', None) == 429)
    
    def _is_validation_error(self, error: Exception) -> bool:
        return (hasattr(error, 'status_code') and getattr(error, 'status_code') == 422) or \
               isinstance(error, models.HTTPValidationError)

class MistralMetadataExtractor(MetadataExtractor):
    def _call_metadata_api(self, prompt: str, model: str = "mistral-large-latest") -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.ai_client.chat.complete(
            model=model, 
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()

class MistralClient(AIClient):
    def __init__(self, api_key):
        super().__init__()
        self.client = Mistral(api_key)
        self.asr_corrector = ASRCorrector(self)
        self.rate_limiter = MistralRateLimiter(min_call_interval=2.0)
        self.parser = ResponseParser()
        self.metadata_extractor = MistralMetadataExtractor(
            self.client, self.rate_limiter
        )
    
    def ask_correction(self, transcription, model, custom_prompt=None, smart_metadata=None):
        min_delay = 0.5

        def perform_correction():
            if model in ["mistral-large-latest"]:
                return self._correct_with_asr(transcription, custom_prompt, smart_metadata, model)
            else:
                return self._correct_directly(transcription, custom_prompt, smart_metadata, model)
        
        result = self.rate_limiter.execute_with_retry(
            perform_correction,
            fallback_value=transcription
        )
        
        time.sleep(min_delay)
        return result

    def _correct_with_asr(self, transcription, custom_prompt, smart_metadata, model):
        content, metadata_para = self.asr_corrector.preprocess(transcription)
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        
        contextual_prompt = self._build_contextual_prompt(
            content, custom_prompt, smart_metadata, model
        )
        print(contextual_prompt)
        messages = [{"role": "user", "content": contextual_prompt}]

        chat_response = self.client.chat.complete(
            model=model,
            messages=messages,
        )

        corrected_content = chat_response.choices[0].message.content
        corrected_content = corrected_content.encode('utf-8', errors='ignore').decode('utf-8')
        return self.asr_corrector.postprocess(corrected_content, metadata_para)

    def _correct_directly(self, transcription, custom_prompt, smart_metadata, model):
        transcription_clean = transcription.encode('utf-8', errors='ignore').decode('utf-8')
        
        contextual_prompt = self._build_contextual_prompt(
            transcription_clean, custom_prompt, smart_metadata, model
        )
        messages = [{"role": "user", "content": contextual_prompt}]

        chat_response = self.client.chat.complete(
            model=model,
            messages=messages,
            temperature=0.1
        )

        raw_response = chat_response.choices[0].message.content
        raw_response = raw_response.encode('utf-8', errors='ignore').decode('utf-8')
        return self.asr_corrector.remove_formatting(raw_response)

    def extract_document_metadata(self, full_content):
        return self.metadata_extractor.extract_document_metadata(full_content)

    def _build_contextual_prompt(self, text, custom_prompt, metadata, model):
        has_custom_prompt = custom_prompt and custom_prompt.strip()
        
        context_header = self._build_document_context(metadata)
        
        if has_custom_prompt:
            base_prompt = f"{custom_prompt}\n\nRetorne apenas a transcrição revisada.\n\nTRANSCRIÇÃO ORIGINAL:\n\n{text}"
        else:
            base_prompt = prompt_model_map[model](text)
        
        if context_header:
            return f"{context_header}\n\n{base_prompt}"
        else:
            return base_prompt