import os
import json
from flask import abort, Flask
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


class FileProcesser:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask app instance.")
        app.extensions["file_processer"] = self

    def validate_file(self, file):
        if not file or file.filename == "":
            return abort(400)
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return abort(400)
        return file

    def read_txt_paragraphs(self, filepath):
        for encoding in ("utf-8", "latin-1"):
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue    

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        return paragraphs, content

    def save_file(self, file):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath, filename

    def process(self, file, client, model):
        file = self.validate_file(file)
        filepath, filename = self.save_file(file)
        paragraphs, content = self.read_txt_paragraphs(filepath)

        corrected_paragraphs = [
            client.ask_correction(paragraph, model) for paragraph in paragraphs
        ]

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
