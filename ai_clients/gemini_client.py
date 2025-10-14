import time
from google import genai
from flask import abort
from prompts import prompt_model_map
from .ai_client import AIClient
from services.rate_limiter import RateLimiter
from services.asr_corrector import ASRCorrector

class GeminiRateLimiter(RateLimiter):
    def __init__(self):
        super().__init__(min_call_interval=2.0)
        self.last_minute_calls = 0
        self.minute_window_start = time.time()
    
    def enforce_gemini_limits(self):      
        current_time = time.time()
        if current_time - self.minute_window_start >= 60:
            self.last_minute_calls = 0
            self.minute_window_start = current_time

        if self.last_minute_calls >= 60:
            sleep_time = 60 - (current_time - self.minute_window_start)
            if sleep_time > 0:
                print(f"Gemini rate limit: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
            self.last_minute_calls = 0
            self.minute_window_start = time.time()
        
        super().enforce_rate_limit()
        self.last_minute_calls += 1

class GeminiClient(AIClient):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.asr_corrector = ASRCorrector(self)
        self.rate_limiter = GeminiRateLimiter()
        self.max_chunk_size = 20000

    def ask_correction(self, transcription, model, custom_prompt=None, smart_metadata=None):
        # Pré-processamento com ASRCorrector (ignora smart_metadata)
        content, metadata_para = self.asr_corrector.preprocess(transcription)
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        
        chunks = self._split_into_chunks(content)
        corrected_chunks = []
        
        for i, chunk in enumerate(chunks):
            corrected_chunk = self._process_chunk(chunk, model, custom_prompt, i, len(chunks))
            corrected_chunks.append(corrected_chunk)
        
        corrected_content = "".join(corrected_chunks)
        corrected_content = corrected_content.encode('utf-8', errors='ignore').decode('utf-8')
        final_result = self.asr_corrector.postprocess(corrected_content, metadata_para)
        
        return final_result
    
    def _split_into_chunks(self, text):
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= self.max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _process_chunk(self, chunk, model, custom_prompt, chunk_index, total_chunks):
        prompt = custom_prompt if custom_prompt else prompt_model_map[model](chunk)
        
        if not custom_prompt and total_chunks > 1:
            progress_info = f" [Part {chunk_index + 1}/{total_chunks}]"
            prompt = prompt + progress_info
        
        def perform_correction():
            self.rate_limiter.enforce_gemini_limits()
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        
        result = self.rate_limiter.execute_with_retry(
            perform_correction,
            fallback_value=chunk,
            max_attempts=3,
            min_delay=1.0 
        )
        
        return result
    
    def get_usage_info(self):
        return self.rate_limiter.get_remaining_calls()
    
    def extract_document_metadata(self, full_content):
        return {
            "entities": ["transcrição", "gemini"],
            "document_type": "conversa gravada",
            "main_topic": "discussão geral", 
            "source": "gemini_fallback"
        }