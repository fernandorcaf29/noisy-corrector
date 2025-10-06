from redlines import Redlines
from flask import Flask
from typing import List, Dict, Tuple

class ComparisonGenerator:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask app instance.")
        app.extensions["comparison_generator"] = self

    def generate_separate_diffs(self, 
                              reference_lines: List[str], 
                              original_lines: List[str], 
                              corrected_lines: List[str]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        diff_trans = []
        diff_corr = []
        
        for ref, orig, corr in zip(reference_lines, original_lines, corrected_lines):

            diff_original = Redlines(ref, orig, markdown_style="custom_css")
            diff_trans.append({"markdown_diff": diff_original.output_markdown})
            
            diff_corrected = Redlines(ref, corr, markdown_style="custom_css")
            diff_corr.append({"markdown_diff": diff_corrected.output_markdown})
        
        return diff_trans, diff_corr