import re
from typing import Dict, Tuple, Any

class ASRCorrector:
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def preprocess(self, text: str) -> Tuple[str, Dict[str, Any]]:
        metadata = {
            'speaker_lines': {},
            'original_text': text
        }
        
        lines = text.split('\n')
        speaker_pattern = r'^([a-zA-ZÀ-ÿ0-9\s]+:)(\s*)(.*)'
        
        for i, line in enumerate(lines):
            speaker_match = re.match(speaker_pattern, line, re.IGNORECASE)
            if speaker_match:
                metadata['speaker_lines'][i] = (
                    speaker_match.group(1),
                    speaker_match.group(2),
                    speaker_match.group(3)
                )
        
        content_lines = []
        for i, line in enumerate(lines):
            if i in metadata['speaker_lines']:
                content_lines.append(metadata['speaker_lines'][i][2])
            else:
                content_lines.append(line)
        
        content = '\n'.join(content_lines)
        return content, metadata
    
    def remove_formatting(self, text: str) -> str:
        formatting_patterns = [
            r'\*\*(.*?)\*\*', r'__(.*?)__', r'\*(.*?)\*', 
            r'_(.*?)_', r'`(.*?)`', r'~~(.*?)~~'
        ]
        
        for pattern in formatting_patterns:
            text = re.sub(pattern, r'\1', text)
        
        return text.strip()
    
    def postprocess(self, corrected_content: str, metadata: Dict[str, Any]) -> str:
        clean_content = self.remove_formatting(corrected_content)
        processed_lines = []
        for line in clean_content.split('\n'):
            speaker_match = re.match(r'^([a-zA-ZÀ-ÿ0-9\s]+:)(\s*)(.*)', line, re.IGNORECASE)
            if speaker_match:
                processed_lines.append(speaker_match.group(3))
            else:
                processed_lines.append(line)
        
        clean_content_processed = '\n'.join(processed_lines)
        
        original_lines = metadata['original_text'].split('\n')
        restored_lines = clean_content_processed.split('\n')
        
        reconstructed_lines = []
        restored_idx = 0
        
        for i, original_line in enumerate(original_lines):
            if not original_line.strip():
                reconstructed_lines.append('')
                continue
                
            if i in metadata['speaker_lines']:
                speaker, space, original_content = metadata['speaker_lines'][i]
                if restored_idx < len(restored_lines):
                    content_only = restored_lines[restored_idx]
                    reconstructed_lines.append(speaker + space + content_only)
                    restored_idx += 1
                else:
                    reconstructed_lines.append(original_line)
            else:
                if restored_idx < len(restored_lines):
                    reconstructed_lines.append(restored_lines[restored_idx])
                    restored_idx += 1
                else:
                    reconstructed_lines.append(original_line)
        
        return '\n'.join(reconstructed_lines)