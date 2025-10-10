import re
from typing import List, Dict, Any

class ResponseParser:
    ENTITIES_PATTERN = re.compile(r'ENTIDADES:\s*([^\n]+?)(?=\s*TIPO:|\n|$)', re.IGNORECASE | re.DOTALL)
    TYPE_PATTERN = re.compile(r'TIPO:\s*([^\n]+?)(?=\s*TEMA:|\n|$)', re.IGNORECASE)
    TOPIC_PATTERN = re.compile(r'TEMA:\s*([^\n]+?)(?=\s*$|\n)', re.IGNORECASE)
    
    @staticmethod
    def parse_metadata_response(response: str) -> Dict[str, Any]:
        entities = []
        doc_type = "unknown"
        main_topic = "unknown"
        
        try:
            clean_response = re.sub(r'[`*]', '', response)
            clean_response = clean_response.strip()
            
            entities = ResponseParser._extract_entities(clean_response)
            doc_type = ResponseParser._extract_document_type(clean_response)
            main_topic = ResponseParser._extract_main_topic(clean_response)
                
        except Exception as e:
            print(f"Parse error: {e}")
        
        return {
            "entities": entities,
            "document_type": doc_type,
            "main_topic": main_topic,
            "source": "ia_analysis"
        }
    
    @staticmethod
    def _extract_entities(text: str) -> List[str]:
        entities_match = ResponseParser.ENTITIES_PATTERN.search(text)
        if entities_match:
            entities_str = entities_match.group(1).strip()
            entities = [
                e.strip() for e in entities_str.split(',') 
                if e.strip() and len(e.strip()) > 1
            ]
            return entities
        
        return ResponseParser._extract_entities_fallback(text)
    
    @staticmethod
    def _extract_entities_fallback(text: str) -> List[str]:
        entities = []
        try:
            lines = text.split('\n')
            for line in lines:
                if line.strip().upper().startswith('ENTIDADES:'):
                    entities_str = line.split(':', 1)[1].strip()
                    entities = [e.strip() for e in entities_str.split(',') if e.strip()]
                    break
        except Exception as e:
            print(f"Entities fallback failed: {e}")
        
        return entities
    
    @staticmethod
    def _extract_document_type(text: str) -> str:
        type_match = ResponseParser.TYPE_PATTERN.search(text)
        if type_match:
            doc_type = type_match.group(1).strip().lower()
            return doc_type
        return "unknown"
    
    @staticmethod
    def _extract_main_topic(text: str) -> str:
        topic_match = ResponseParser.TOPIC_PATTERN.search(text)
        if topic_match:
            main_topic = topic_match.group(1).strip().lower()
            return main_topic
        return "unknown"