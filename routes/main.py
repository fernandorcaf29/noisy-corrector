from flask import Blueprint, Response, json, render_template, request, redirect, url_for, jsonify, stream_with_context
from werkzeug.utils import secure_filename
import os
import asyncio
import time
import uuid
from services.file_processing import read_txt_paragraphs
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from services.metrics import calculate_bert_score, calculate_bleu
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

@bp.route('/process_evaluation', methods=['POST'])
def process_evaluation():
    if 'reference_file' not in request.files or 'test_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Arquivos não fornecidos'}), 400

    reference_file = request.files['reference_file']
    test_file = request.files['test_file']

    if reference_file.filename == '' or test_file.filename == '':
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo selecionado'}), 400

    ref_path = None
    test_path = None

    try:
        unique_id = str(uuid.uuid4())[:8]
        ref_filename = f"ref_{unique_id}_{secure_filename(reference_file.filename)}"
        test_filename = f"test_{unique_id}_{secure_filename(test_file.filename)}"
        ref_path = os.path.join(UPLOAD_FOLDER, ref_filename)
        test_path = os.path.join(UPLOAD_FOLDER, test_filename)
        reference_file.save(ref_path)
        test_file.save(test_path)

        # Ler arquivos
        reference_lines = read_txt_paragraphs(ref_path)
        test_lines = read_txt_paragraphs(test_path)

        if len(reference_lines) != len(test_lines):
            return jsonify({
                'status': 'error',
                'message': f'Arquivos têm número diferente de linhas. Referência: {len(reference_lines)}, Teste: {len(test_lines)}'
            }), 400

        results = []
        total_bleu_original = total_bleu_corrected = 0
        total_bert_original = total_bert_corrected = 0
        processed_count = 0
        total_lines = len(reference_lines)

        print(f"Iniciando avaliação de {total_lines} linhas...")

        for i, (ref_line, test_line) in enumerate(zip(reference_lines, test_lines)):
            ref_line = ref_line.strip()
            test_line = test_line.strip()
            if not ref_line or not test_line:
                continue

            try:
                corrected_line = ask_mistral(test_line)

                # Calcular métricas
                bleu_original = calculate_bleu(ref_line, test_line)
                bleu_corrected = calculate_bleu(ref_line, corrected_line)
                bert_original = calculate_bert_score(ref_line, test_line)
                bert_corrected = calculate_bert_score(ref_line, corrected_line)

                total_bleu_original += bleu_original
                total_bleu_corrected += bleu_corrected
                total_bert_original += bert_original
                total_bert_corrected += bert_corrected
                processed_count += 1

                print(f"{processed_count}/{total_lines} linhas processadas...")

                results.append({
                    'index': i + 1,
                    'reference': ref_line,
                    'original': test_line,
                    'corrected': corrected_line,
                    'bleu_original': round(bleu_original * 100, 2),
                    'bleu_corrected': round(bleu_corrected * 100, 2),
                    'bert_original': round(bert_original * 100, 2),
                    'bert_corrected': round(bert_corrected * 100, 2),
                    'bleu_diff': round((bleu_corrected - bleu_original) * 100, 2),
                    'bert_diff': round((bert_corrected - bert_original) * 100, 2)
                })

            except Exception as e:
                results.append({
                    'index': i + 1,
                    'reference': ref_line,
                    'original': test_line,
                    'corrected': f"[ERRO: {str(e)}]",
                    'bleu_original': 0,
                    'bleu_corrected': 0,
                    'bert_original': 0,
                    'bert_corrected': 0,
                    'bleu_diff': 0,
                    'bert_diff': 0,
                    'error': True
                })

        # Calcular médias
        avg_bleu_original = (total_bleu_original / processed_count * 100) if processed_count > 0 else 0
        avg_bleu_corrected = (total_bleu_corrected / processed_count * 100) if processed_count > 0 else 0
        avg_bert_original = (total_bert_original / processed_count * 100) if processed_count > 0 else 0
        avg_bert_corrected = (total_bert_corrected / processed_count * 100) if processed_count > 0 else 0

        print(f"Avaliação concluída! {processed_count}/{total_lines} linhas processadas")

        return jsonify({
            'status': 'success',
            'total_lines': total_lines,
            'processed_count': processed_count,
            'results': results,
            'summary': {
                'avg_bleu_original': round(avg_bleu_original, 2),
                'avg_bleu_corrected': round(avg_bleu_corrected, 2),
                'avg_bert_original': round(avg_bert_original, 2),
                'avg_bert_corrected': round(avg_bert_corrected, 2),
                'avg_bleu_improvement': round(avg_bleu_corrected - avg_bleu_original, 2),
                'avg_bert_improvement': round(avg_bert_corrected - avg_bert_original, 2)
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        # Limpar arquivos temporários
        try:
            if ref_path and os.path.exists(ref_path):
                os.remove(ref_path)
            if test_path and os.path.exists(test_path):
                os.remove(test_path)
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários: {e}")