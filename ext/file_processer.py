import json
from flask import abort
import os
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import Flask
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileProcesser:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask app instance.")
        app.extensions["file_processer"] = self

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
        paragraphs, content = self.read_txt_paragraphs(filepath)

        corrected_paragraphs = [""] * len(paragraphs)  # Inicializa com strings vazias

        def correct_paragraph(paragraph, index):
            try:
                corrected = client.ask_correction(paragraph, model, custom_prompt)
                return corrected, index
            except Exception as e:
                print(f"Error correcting paragraph {index}: {e}")
                return paragraphs[index], index  # Retorna o original em caso de erro

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for i, paragraph in enumerate(paragraphs):
                futures.append(executor.submit(correct_paragraph, paragraph, i))

            for future in as_completed(futures):
                corrected, index = future.result()
                corrected_paragraphs[index] = corrected

        corrected_content = "\n\n".join(corrected_paragraphs)

        return {
            "input_file": {
                "paragraphs": paragraphs,
                "content": content,
                "filename": filename,
            },
            "output_file": {
                "paragraphs": corrected_paragraphs,
                "content": corrected_content,
                "filename": f"corrected_{filename}",
            },
        }
