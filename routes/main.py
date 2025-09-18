from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import asyncio
from services.file_processing import read_txt_paragraphs
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from services.mistral_client import ask_mistral
from redlines import Redlines
bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def home():
    return render_template('index.html', title='Noisy Corrector')

@bp.route('/playground', methods=['GET'])
def playground():
    return render_template('playground.html', title='Playground - Noisy Corrector')

@bp.route('/process', methods=['POST'])
def process():
    if 'document' not in request.files:
        return redirect(url_for('main.home'))

    file = request.files['document']

    if file.filename == '':
        return redirect(url_for('main.home'))

    if file and '.' in file.filename and \
       file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        paragraphs = read_txt_paragraphs(filepath)

        corrected_paragraphs = []

        for p in paragraphs:
            corrected_paragraphs.append(ask_mistral(p))
        
        redlines = []

        for orig, corrected in zip(paragraphs, corrected_paragraphs):
            redline = Redlines(orig, corrected, markdown_style='custom_css')
            redlines.append({
                'markdown_diff': redline.output_markdown
            })
        
        content = '\n\n'.join(corrected_paragraphs)
        
        return jsonify({
            'status': 'success',
            'redlines': redlines,
            'file_content': content,
            'filename': f'corrected_{filename}'
        })

    
    return redirect(url_for('main.home'))