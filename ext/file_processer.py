import json
from flask import abort
import os
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import Flask


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

    def read_json_and_extract_text(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON data should be an array of objects")

        return " ".join(item["text"] for item in data if "text" in item)

    def save_file(self, file):
        filename = secure_filename(file.filename)

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        return filepath, filename

    def process(self, file, client, model):
        file = self.validate_file(file)

        filepath, filename = self.save_file(file)

        paragraphs, content = self.read_txt_paragraphs(filepath)

        corrected_paragraphs = []

        for paragraph in paragraphs:
            corrected_paragraph = client.ask_correction(paragraph, model)
            corrected_paragraphs.append(corrected_paragraph)

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
