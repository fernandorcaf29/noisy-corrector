import time
import random
from google import genai
from google.api_core import exceptions
from prompts import prompt_model_map
from .ai_client import AIClient
from services.rate_limiter import RateLimiter
from services.asr_corrector import ASRCorrector
from services.metadata.metadata_extractor import MetadataExtractor

class GeminiRateLimiter(RateLimiter):
    def __init__(self):
        super().__init__(min_call_interval=4.0)
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

class GeminiMetadataExtractor(MetadataExtractor):
    def _call_metadata_api(self, prompt: str, model: str) -> str:
        max_retries = 5
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.ai_client.models.generate_content(
                    model=model, 
                    contents=prompt
                )
                return response.text.strip()
            except exceptions.ServiceUnavailable as e:
                if attempt == max_retries - 1:
                    print(f"Error extracting metadata with Gemini after {max_retries} attempts: {e}")
                    return ""
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Gemini model overloaded, retry {attempt + 1}/{max_retries} in {delay:.1f}s")
                time.sleep(delay)
            except Exception as e:
                print(f"Error extracting metadata with Gemini: {e}")
                return ""
        
        return ""

class GeminiClient(AIClient):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.asr_corrector = ASRCorrector(self)
        self.rate_limiter = GeminiRateLimiter()
        self.max_chunk_size = 15000
        self.metadata_extractor = GeminiMetadataExtractor(
            self.client,  
            self.rate_limiter
        )

    def ask_correction(self, transcription, model, custom_prompt=None, smart_metadata=None):
        content, metadata_para = self.asr_corrector.preprocess(transcription)
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        corrected_paragraphs = self._process_paragraph_chunks(paragraphs, model, custom_prompt, smart_metadata)
        
        corrected_content = "".join(corrected_paragraphs)
        final_result = self.asr_corrector.postprocess(corrected_content, metadata_para)
        return final_result

    def _process_paragraph_chunks(self, paragraphs, model, custom_prompt, metadata):
        """Processa múltiplos parágrafos em chunks respeitando max_chunk_size."""
        corrected_paragraphs = [""] * len(paragraphs)

        def correct_chunk(chunk_text, paragraph_indices):
            max_retries = 5
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    chunk_clean = chunk_text.encode('utf-8', errors='ignore').decode('utf-8').strip()
                    if not chunk_clean:
                        return [""] * len(paragraph_indices)

                    self.rate_limiter.enforce_gemini_limits()
                    
                    contextual_prompt = self._build_contextual_prompt(
                        chunk_clean, custom_prompt, metadata, model
                    )
                    
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contextual_prompt,
                    )
                    corrected = response.text
                    corrected = corrected.encode('utf-8', errors='ignore').decode('utf-8').strip() if corrected else chunk_clean

                    split_corrected = corrected.split("\n\n")
                    if len(split_corrected) != len(paragraph_indices):
                        split_corrected = [corrected] * len(paragraph_indices)

                    return split_corrected
                    
                except exceptions.ServiceUnavailable as e:
                    if attempt == max_retries - 1:
                        print(f"Error processing chunk after {max_retries} attempts: {e}")
                        safe_chunk = chunk_text.encode('utf-8', errors='ignore').decode('utf-8')
                        return [safe_chunk] * len(paragraph_indices)
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Gemini model overloaded, retry {attempt + 1}/{max_retries} in {delay:.1f}s")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    safe_chunk = chunk_text.encode('utf-8', errors='ignore').decode('utf-8')
                    return [safe_chunk] * len(paragraph_indices)

        chunk_text = ""
        chunk_indices = []

        for i, paragraph in enumerate(paragraphs):
            paragraph_safe = paragraph.encode('utf-8', errors='ignore').decode('utf-8').strip()
            if not paragraph_safe:
                corrected_paragraphs[i] = ""
                continue

            if len(chunk_text) + len(paragraph_safe) + 2 <= self.max_chunk_size:
                chunk_text = f"{chunk_text}\n\n{paragraph_safe}" if chunk_text else paragraph_safe
                chunk_indices.append(i)
            else:
                corrected_chunk = correct_chunk(chunk_text, chunk_indices)
                for idx, para_idx in enumerate(chunk_indices):
                    corrected_paragraphs[para_idx] = corrected_chunk[idx]

                chunk_text = paragraph_safe
                chunk_indices = [i]

        if chunk_indices:
            corrected_chunk = correct_chunk(chunk_text, chunk_indices)
            for idx, para_idx in enumerate(chunk_indices):
                corrected_paragraphs[para_idx] = corrected_chunk[idx]

        return corrected_paragraphs

    def _build_contextual_prompt(self, text, custom_prompt, metadata, model):
        """Constroi prompt contextual com metadados para Gemini"""
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

    def extract_document_metadata(self, full_content, model):
        """Extrai metadados do documento usando Gemini"""
        return self.metadata_extractor.extract_document_metadata(full_content, model)