from typing import Dict, Any
from services.rate_limiter import RateLimiter
from .response_parser import ResponseParser
from prompts import get_metadata_extraction_prompt

class MetadataExtractor:
    def __init__(self, ai_client, rate_limiter: RateLimiter):
        self.ai_client = ai_client
        self.rate_limiter = rate_limiter
        self.parser = ResponseParser()
        self.document_metadata_cache = {}
    
    def extract_document_metadata(self, full_content: str, 
                                model: str = "mistral-large-latest") -> Dict[str, Any]:
        if not full_content or not full_content.strip():
            return self._get_fallback_metadata()
            
        cache_key = hash(full_content[:1000])
        if cache_key in self.document_metadata_cache:
            return self.document_metadata_cache[cache_key]
        
        sample_text = self._prepare_sample_text(full_content)
        prompt = get_metadata_extraction_prompt(sample_text)
        
        def analyze_document():
            self.rate_limiter.enforce_rate_limit()
            return self._call_metadata_api(prompt, model)
        
        result = self.rate_limiter.execute_with_retry(
            analyze_document, 
            fallback_value=None
        )
        
        if result is None:
            return self._get_fallback_metadata()
        
        print(f"Raw AI response: {result}")
        metadata = self.parser.parse_metadata_response(result)
        self.document_metadata_cache[cache_key] = metadata
        
        return metadata
    
    def _prepare_sample_text(self, full_content: str) -> str:
        lines = [line.strip() for line in full_content.split('\n') if line.strip()]
        if not lines:
            return ""
            
        sample_lines = lines[:10]
        if len(lines) > 20:
            sample_lines.extend(lines[15:18])
        
        return '\n'.join(sample_lines)
    
    def _call_metadata_api(self, prompt: str, model: str) -> str:
        raise NotImplementedError("Subclasses must implement _call_metadata_api")
    
    def _get_fallback_metadata(self) -> Dict[str, Any]:
        return {
            "entities": ["transcrição", "entrevista"],
            "document_type": "conversa gravada", 
            "main_topic": "discussão geral",
            "source": "fallback_enhanced"
        }