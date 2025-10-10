from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import re

class AIClient(ABC):
    def __init__(self):
        self.document_metadata_cache = {}
    
    @abstractmethod
    def ask_correction(self, transcription, model, custom_prompt=None, smart_metadata=None):
        pass
    
    @abstractmethod
    def extract_document_metadata(self, full_content: str) -> Dict[str, Any]:
        pass
    
    def _build_document_context(self, metadata: Optional[Dict]) -> str:
        if not metadata or metadata.get('source') == 'fallback':
            return ""
        
        context_parts = []
        
        if metadata.get('entities'):
            clean_entities = []
            for entity in metadata['entities'][:6]:
                clean_entity = re.sub(r'\s*\([^)]*\)', '', entity).strip()
                if clean_entity and len(clean_entity) > 2:
                    clean_entities.append(clean_entity)
            
            if clean_entities:
                context_parts.append(f"ENTIDADES DO TEXTO: {', '.join(clean_entities)}")
        
        doc_type = metadata.get('document_type', 'unknown')
        if doc_type != 'unknown':
            if 'entrevista política' in doc_type:
                display_type = 'ENTREVISTA POLÍTICA'
            elif 'debate' in doc_type:
                display_type = 'DEBATE'
            else:
                display_type = doc_type.upper()
            context_parts.append(f"TIPO: {display_type}")
        
        main_topic = metadata.get('main_topic', 'unknown')
        if main_topic != 'unknown':
            formatted_topic = ' '.join(word.capitalize() for word in main_topic.split())
            context_parts.append(f"ASSUNTO: {formatted_topic}")
        
        if context_parts:
            return "CONTEXTO IDENTIFICADO:\n" + "\n".join(f"• {item}" for item in context_parts)
        
        return ""