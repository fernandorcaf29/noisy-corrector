import time
import re
from mistralai import Mistral
from prompts import prompt_model_map
from .ai_client import AIClient
from flask import abort
from mistralai import models
from services.asr_corrector import ASRCorrector

class MistralClient(AIClient):
    def __init__(self, api_key):
        self.client = Mistral(api_key)
        self.asr_corrector = ASRCorrector(self)
        self.document_metadata_cache = {} 
        self.last_api_call = 0
        self.min_call_interval = 2.0 

    def ask_correction(self, transcription, model, custom_prompt=None, metadata=None):
        min_delay = 0.5
        max_delay = 3
        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            try:
                if model in ["mistral-large-latest"]:
                    content, metadata_para = self.asr_corrector.preprocess(transcription)
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')
                    
                    contextual_prompt = self._build_contextual_prompt(
                        content, custom_prompt, metadata, model
                    )
                    messages = [{"role": "user", "content": contextual_prompt}]

                    chat_response = self.client.chat.complete(
                        model=model,
                        messages=messages,
                    )

                    corrected_content = chat_response.choices[0].message.content
                    corrected_content = corrected_content.encode('utf-8', errors='ignore').decode('utf-8')
                    final_text = self.asr_corrector.postprocess(corrected_content, metadata_para)
                else:
                    transcription_clean = transcription.encode('utf-8', errors='ignore').decode('utf-8')
                    
                    contextual_prompt = self._build_contextual_prompt(
                        transcription_clean, custom_prompt, metadata, model
                    )
                    
                    messages = [{"role": "user", "content": contextual_prompt}]

                    chat_response = self.client.chat.complete(
                        model=model,
                        messages=messages,
                        temperature=0.1
                    )

                    raw_response = chat_response.choices[0].message.content
                    raw_response = raw_response.encode('utf-8', errors='ignore').decode('utf-8')
                    final_text = self.asr_corrector.remove_formatting(raw_response)
                
                time.sleep(min_delay)
                return final_text

            except models.HTTPValidationError:
                abort(422)

            except models.SDKError as e:
                if e.status_code == 429:
                    delay = min(max(min_delay * (2 ** attempt), min_delay), max_delay)
                    print(f"[429] Too Many Requests. Attempt {attempt+1}/{max_attempts}, sleeping {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    continue
                print(f"SDKError: {e}")
                return transcription
            except Exception as e:
                print(f"Unexpected error: {e}")
                return transcription 
        
        return transcription

    def extract_document_metadata(self, full_content):
        if not full_content or not full_content.strip():
            return self._get_fallback_metadata()
            
        cache_key = hash(full_content[:1000])
        if cache_key in self.document_metadata_cache:
            return self.document_metadata_cache[cache_key]
        
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            print(f"Aguardando {sleep_time:.1f}s para próxima análise...")
            time.sleep(sleep_time)
        
        lines = [line.strip() for line in full_content.split('\n') if line.strip()]
        if not lines:
            return self._get_fallback_metadata()
            
        sample_lines = lines[:10]
        if len(lines) > 20:
            sample_lines.extend(lines[15:18])
        
        sample_text = '\n'.join(sample_lines)

        prompt = f"""
        ANALISE ESTE TEXTO E IDENTIFIQUE:

        **ENTIDADES PRINCIPAIS**: Nomes de pessoas, lugares, instituições, organizações (máximo 5)
        **TIPO DE CONVERSA**: entrevista, debate, discurso, reunião, aula, podcast, etc.
        **TEMA CENTRAL**: Assunto principal em 3-6 palavras

        **FORMATO EXATO PARA RESPOSTA**:
        ENTIDADES: nome1, nome2, nome3, nome4, nome5, nome6
        TIPO: [tipo específico da conversa]
        TEMA: [tema principal resumido]

        **EXEMPLOS CORRETOS**:
        ENTIDADES: entrevistadora Juliana, candidato Bruno Lessa, Niterói, UFF, Prefeitura, Podemos
        TIPO: entrevista política eleitoral
        TEMA: propostas para proteção animal

        ENTIDADES: professor Carlos, alunos, escola municipal, secretaria educação
        TIPO: aula sobre educação ambiental  
        TEMA: sustentabilidade nas escolas

        ENTIDADES: médica Dra Silva, pacientes, hospital municipal
        TIPO: consulta médica gravada
        TEMA: cuidados com saúde preventiva

        **TEXTO PARA ANALISAR**:
        {sample_text}
        """
        
        try:
            self.last_api_call = time.time()
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model="mistral-large-latest", 
                messages=messages,
                temperature=0.1,
            )
         
            result = response.choices[0].message.content.strip()
            metadata = self._parse_metadata_response_improved(result)
            self.document_metadata_cache[cache_key] = metadata
            return metadata
            
        except models.SDKError as e:
            if e.status_code == 429:
                print("Reached Rate limit, using fallback")
            else:
                print(f"Erro API: {e}")
            return self._get_fallback_metadata()
        except Exception as e:
            print(f"Analysis failed: {e}")
            return self._get_fallback_metadata()
    
    def _parse_metadata_response_improved(self, response):
        entities = []
        doc_type = "unknown"
        main_topic = "unknown"
        
        try:
            clean_response = re.sub(r'[`*]', '', response) 
            clean_response = clean_response.strip()
            entities_match = re.search(r'ENTIDADES:\s*([^\n]+?)(?=\s*TIPO:|\n|$)', clean_response, re.IGNORECASE | re.DOTALL)
            if entities_match:
                entities_str = entities_match.group(1).strip()
                
                entities = [
                    e.strip() for e in entities_str.split(',') 
                    if e.strip() and len(e.strip()) > 1
                ]
            
            type_match = re.search(r'TIPO:\s*([^\n]+?)(?=\s*TEMA:|\n|$)', clean_response, re.IGNORECASE)
            if type_match:
                doc_type = type_match.group(1).strip().lower()
            
            topic_match = re.search(r'TEMA:\s*([^\n]+?)(?=\s*$|\n)', clean_response, re.IGNORECASE)
            if topic_match:
                main_topic = topic_match.group(1).strip().lower()
            
            if not entities and "ENTIDADES:" in clean_response:
                entities = self._extract_entities_fallback(clean_response)
                
        except Exception as e:
            print(f"Erro no parse: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            "entities": entities,
            "document_type": doc_type,
            "main_topic": main_topic,
            "source": "ia_analysis"
        }

    def _extract_entities_fallback(self, text):
        entities = []
        try:
            lines = text.split('\n')
            for line in lines:
                if line.strip().upper().startswith('ENTIDADES:'):
                    entities_str = line.split(':', 1)[1].strip()
                    entities = [e.strip() for e in entities_str.split(',') if e.strip()]
                    break
        except Exception as e:
            print(f"Fallback de entidades falhou: {e}")
        
        return entities

    def _apply_intelligent_fallback(self, text, entities, doc_type, main_topic):
        text_lower = text.lower()
        
        type_keywords = {
            'entrevista': 'entrevista',
            'debate': 'debate', 
            'aula': 'aula',
            'reunião': 'reunião',
            'palestra': 'palestra',
            'discussão': 'discussão',
            'podcast': 'podcast',
            'live': 'transmissão ao vivo',
            'cobertura': 'cobertura jornalística'
        }
        
        for keyword, inferred_type in type_keywords.items():
            if keyword in text_lower:
                doc_type = inferred_type
                break
        
        if main_topic == "unknown" and entities:
            main_topic = f"discussão sobre {', '.join(entities[:2])}"
        
        return doc_type, main_topic
    
    def _get_fallback_metadata(self):
        return {
            "entities": ["transcrição", "entrevista"],
            "document_type": "conversa gravada",
            "main_topic": "discussão geral",
            "source": "fallback_enhanced"
        }

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

    def _build_document_context(self, metadata):
        if not metadata or metadata.get('source') == 'fallback':
            return ""
        
        context_parts = []
        
        if metadata.get('entities'):
            clean_entities = []
            for entity in metadata['entities'][:4]:
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
            main_topic = ' '.join(word.capitalize() for word in main_topic.split())
            context_parts.append(f"ASSUNTO: {main_topic}")
        
        if context_parts:
            return "CONTEXTO IDENTIFICADO:\n" + "\n".join(f"• {item}" for item in context_parts)
        
        return ""