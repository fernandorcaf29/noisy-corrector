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

    def generate_diff(self, original, corrected):
        diff = []

        for original, corrected in zip(original, corrected):
            redline = Redlines(original, corrected, markdown_style="custom_css")
            diff.append({"markdown_diff": redline.output_markdown})

        return diff
