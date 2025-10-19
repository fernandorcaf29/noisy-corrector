from redlines import Redlines
from flask import Flask


class DiffGenerator:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask app instance.")
        app.extensions["diff_generator"] = self

    def generate_diff(self, original_paragraphs, corrected_paragraphs):
        return [
            {"markdown_diff": Redlines(o, c, markdown_style="custom_css").output_markdown}
            for o, c in zip(original_paragraphs, corrected_paragraphs)
        ]
