import time
from flask import abort
import os
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import Flask
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileProcessor:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask app instance.")
        app.extensions["file_processor"] = self

    def validate_file(self, file):
        if file.filename == "":
            return abort(400)

        if not (
            file
            and "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        ):
            return abort(400)

        return file

    def read_txt_paragraphs(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="latin-1") as f:
                content = f.read()

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        return paragraphs, content

    def save_file(self, file):
        filename = secure_filename(file.filename)

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        return filepath, filename

    def process(self, file, client, model, custom_prompt=None):
        file = self.validate_file(file)
        filepath, filename = self.save_file(file)
        paragraphs, full_content = self.read_txt_paragraphs(filepath)
        
        # Extrair metadados apenas para Mistral (Gemini não usa)
        document_metadata = None
        if model.startswith('mistral'):
            document_metadata = client.extract_document_metadata(full_content)
        else:
            # Para Gemini, usar metadados básicos
            document_metadata = {
                "entities": ["transcrição", "gemini"],
                "document_type": "conversa gravada",
                "main_topic": "discussão geral",
                "source": "gemini_fallback"
            }

        corrected_paragraphs = [""] * len(paragraphs)

        def correct_paragraph(paragraph, index, metadata):
            try:
                if not paragraph or not paragraph.strip():
                    return paragraph or "", index
                    
                paragraph_clean = paragraph.encode('utf-8', errors='ignore').decode('utf-8').strip()
                
                if not paragraph_clean:
                    return "", index
                    
                corrected = client.ask_correction(paragraph_clean, model, custom_prompt, metadata)
                
                if corrected and corrected.strip():
                    corrected = corrected.encode('utf-8', errors='ignore').decode('utf-8').strip()
                else:
                    corrected = paragraph_clean
                    
                return corrected, index                
            except Exception as e:
                safe_paragraph = paragraph.encode('utf-8', errors='ignore').decode('utf-8') if paragraph else ""
                return safe_paragraph, index

        # Estratégia diferente para Gemini vs Mistral
        if model.startswith('gemini'):
            # Para Gemini: processamento sequencial com delays maiores
            print(f"Processing {len(paragraphs)} paragraphs with Gemini (sequential mode)")
            
            for i, paragraph in enumerate(paragraphs):
                if paragraph and paragraph.strip():
                    safe_paragraph = paragraph.encode('utf-8', errors='ignore').decode('utf-8')
                    corrected, index = correct_paragraph(safe_paragraph, i, document_metadata)
                    corrected_paragraphs[index] = corrected
                    
                    # Delay maior entre requisições para respeitar rate limits do Gemini
                    if i < len(paragraphs) - 1:  # Não esperar após o último
                        time.sleep(4)  # 4 segundos entre requisições (15/min)
                        
                    print(f"Processed paragraph {i+1}/{len(paragraphs)} with Gemini")
                else:
                    corrected_paragraphs[i] = ""
        else:
            # Para Mistral: processamento paralelo (comportamento original)
            print(f"Processing {len(paragraphs)} paragraphs with Mistral (parallel mode)")
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                
                for i, paragraph in enumerate(paragraphs):
                    if paragraph and paragraph.strip():
                        safe_paragraph = paragraph.encode('utf-8', errors='ignore').decode('utf-8')
                        futures.append(executor.submit(
                            correct_paragraph, safe_paragraph, i, document_metadata
                        ))
                    else:
                        corrected_paragraphs[i] = ""

                completed = 0
                for future in as_completed(futures):
                    corrected, index = future.result()
                    corrected_paragraphs[index] = corrected
                    completed += 1
                    
                    # Pequeno delay para Mistral (já tem rate limiting interno)
                    if completed % 3 == 0:
                        time.sleep(0.3)
                        
                    print(f"Processed paragraph {completed}/{len(futures)} with Mistral")

        corrected_content = "\n\n".join(corrected_paragraphs)

        # Adicionar informações de uso se disponível (especialmente para Gemini)
        usage_info = ""
        if hasattr(client, 'get_usage_info'):
            try:
                usage_info = client.get_usage_info()
                print(f"API Usage info: {usage_info}")
            except:
                pass

        return {
            "input_file": {
                "paragraphs": paragraphs,
                "content": full_content,
                "filename": filename,
            },
            "output_file": {
                "paragraphs": corrected_paragraphs,
                "content": corrected_content,
                "filename": f"corrected_{filename}",
            },
            "metadata": document_metadata,
            "usage_info": usage_info,
            "model_used": model
        }

    def get_estimated_processing_time(self, paragraphs_count, model):
        """Estima o tempo de processamento baseado no modelo"""
        if model.startswith('gemini'):
            # Gemini: 4 segundos por parágrafo + overhead
            return paragraphs_count * 4 + 10
        else:
            # Mistral: ~1 segundo por parágrafo em paralelo
            return paragraphs_count * 0.5 + 5