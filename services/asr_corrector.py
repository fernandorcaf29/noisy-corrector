import re
from typing import Dict, Tuple, Any, List

class ASRCorrector:
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def preprocess(self, text: str) -> Tuple[str, Dict[str, Any]]:
        metadata = {
            'speaker_lines': {},
            'original_text': text,
            'uppercase_words_with_context': self._extract_uppercase_with_context(text),
            'original_lines': text.split('\n')
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
    
    def _extract_uppercase_with_context(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extrai palavras maiúsculas com contexto para busca inteligente
        """
        context_map = {}
        lines = text.split('\n')
        speaker_pattern = r'^([a-zA-ZÀ-ÿ0-9\s]+:)(\s*)(.*)'
        
        for line_idx, line in enumerate(lines):
            speaker_match = re.match(speaker_pattern, line, re.IGNORECASE)
            content = speaker_match.group(3) if speaker_match else line
            
            words = content.split()
            uppercase_info = []
            
            for word_idx, word in enumerate(words):
                if word and word[0].isalpha() and word[0].isupper():
                    # Armazena contexto para busca robusta
                    context_before = words[max(0, word_idx-2):word_idx]  # 2 palavras antes
                    context_after = words[word_idx+1:min(len(words), word_idx+3)]  # 2 palavras depois
                    
                    uppercase_info.append({
                        'original_word': word,
                        'original_position': word_idx,
                        'context_before': context_before,
                        'context_after': context_after
                    })
            
            if uppercase_info:
                context_map[str(line_idx)] = uppercase_info
        
        return context_map
    
    def _restore_capitalization_with_context(self, corrected_content: str, metadata: Dict[str, Any]) -> str:
        """
        Restaura maiúsculas usando busca por contexto
        """
        corrected_lines = corrected_content.split('\n')
        
        for line_idx, corrected_line in enumerate(corrected_lines):
            if str(line_idx) not in metadata['uppercase_words_with_context']:
                continue
                
            corrected_words = corrected_line.split()
            uppercase_info = metadata['uppercase_words_with_context'][str(line_idx)]
            
            # Marca palavras já capitalizadas para evitar duplicação
            capitalized_indices = set()
            
            for original_data in uppercase_info:
                original_word = original_data['original_word']
                original_pos = original_data['original_position']
                context_before = original_data['context_before']
                context_after = original_data['context_after']
                
                # Estratégia 1: Tentativa por posição original (mais comum)
                if original_pos < len(corrected_words) and original_pos not in capitalized_indices:
                    current_word = corrected_words[original_pos]
                    if self._words_match(original_word, current_word):
                        corrected_words[original_pos] = self._apply_case(current_word, original_word)
                        capitalized_indices.add(original_pos)
                        continue
                
                # Estratégia 2: Busca por contexto
                best_match_idx = self._find_word_by_context(
                    original_word, context_before, context_after, corrected_words, capitalized_indices
                )
                
                if best_match_idx is not None:
                    corrected_words[best_match_idx] = self._apply_case(corrected_words[best_match_idx], original_word)
                    capitalized_indices.add(best_match_idx)
            
            corrected_lines[line_idx] = ' '.join(corrected_words)
        
        return '\n'.join(corrected_lines)
    
    def _words_match(self, word1: str, word2: str) -> bool:
        """Verifica se duas palavras correspondem (case-insensitive)"""
        return word1.lower() == word2.lower()
    
    def _find_word_by_context(self, target_word: str, context_before: List[str], context_after: List[str], 
                             corrected_words: List[str], excluded_indices: set) -> int:
        """
        Encontra a melhor correspondência baseada no contexto
        """
        best_match_idx = None
        best_score = 0
        
        for idx, word in enumerate(corrected_words):
            if idx in excluded_indices:
                continue
                
            if not self._words_match(target_word, word):
                continue
            
            # Calcula score de contexto
            context_score = 0
            
            # Verifica contexto anterior
            for i, context_word in enumerate(context_before):
                check_idx = idx - len(context_before) + i
                if 0 <= check_idx < len(corrected_words):
                    if self._words_match(context_word, corrected_words[check_idx]):
                        context_score += 0.5
            
            # Verifica contexto posterior
            for i, context_word in enumerate(context_after):
                check_idx = idx + 1 + i
                if check_idx < len(corrected_words):
                    if self._words_match(context_word, corrected_words[check_idx]):
                        context_score += 0.5
            
            if context_score > best_score:
                best_score = context_score
                best_match_idx = idx
        
        return best_match_idx if best_score > 0 else None
    
    def _apply_case(self, current_word: str, original_word: str) -> str:
        """Aplica o padrão de capitalização da palavra original"""
        if original_word.isupper():
            return current_word.upper()
        elif original_word[0].isupper():
            if current_word[0].isalpha():
                return current_word[0].upper() + current_word[1:]
            else:
                for i, char in enumerate(current_word):
                    if char.isalpha():
                        return current_word[:i] + char.upper() + current_word[i+1:]
                        break
        return current_word
    
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
        
        # Aplica capitalização inteligente com contexto
        content_with_case = self._restore_capitalization_with_context(clean_content, metadata)
        
        # Reconstrói com identificadores originais
        corrected_lines = content_with_case.split('\n')
        original_lines = metadata['original_lines']
        
        reconstructed_lines = []
        corrected_idx = 0
        
        for i, original_line in enumerate(original_lines):
            if not original_line.strip():
                reconstructed_lines.append('')
                continue
                
            if i in metadata['speaker_lines']:
                speaker, space, original_content = metadata['speaker_lines'][i]
                if corrected_idx < len(corrected_lines):
                    content_only = corrected_lines[corrected_idx]
                    reconstructed_lines.append(speaker + space + content_only)
                    corrected_idx += 1
                else:
                    reconstructed_lines.append(original_line)
            else:
                if corrected_idx < len(corrected_lines):
                    reconstructed_lines.append(corrected_lines[corrected_idx])
                    corrected_idx += 1
                else:
                    reconstructed_lines.append(original_line)
        
        return '\n'.join(reconstructed_lines)