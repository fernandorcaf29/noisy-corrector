import json
import os
from flask import Blueprint, render_template, request, abort, current_app
from ai_clients.ai_client_factory import AIClientFactory
from services.metrics import calculate_bert_score, calculate_bleu
bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@bp.route('/playground', methods=['GET'])
def playground():
    return render_template('playground.html', title='Playground - Noisy Corrector')

@bp.route("/result", methods=["POST", "GET"])
def result():
    if request.method != "POST":
        return render_template("index.html")

    if "document" not in request.files:
        return abort(400)

    file = request.files["document"]

    if not file:
        return abort(400)

    model = request.form.get("model")

    if not model:
        return abort(400)

    api_key = request.form.get("api_key")

    if not api_key:
        return abort(400)

    client = AIClientFactory.create_client(model, api_key)

    file_processer = current_app.extensions["file_processer"]
    diff_generator = current_app.extensions["diff_generator"]

    files = file_processer.process(file, client, model)
    
    diff = diff_generator.generate_diff(
        files["input_file"]["paragraphs"], files["output_file"]["paragraphs"]
    )

    return render_template(
        "result.html",
        redlines=diff,
        file_content=files["output_file"]["content"],
        filename=files["output_file"]["filename"],
    )


@bp.errorhandler(429)
def too_many_requests(e):
    return (
        render_template(
            "error.html", error_message="Too many requests", error_code=429
        ),
        429,
    )


@bp.errorhandler(400)
def bad_request(e):
    return (
        render_template("error.html", error_message="Bad request", error_code=400),
        400,
    )


@bp.errorhandler(405)
def method_not_allowed(e):
    return (
        render_template(
            "error.html", error_message="Method not allowed", error_code=405
        ),
        405,
    )


@bp.errorhandler(401)
def unauthorized(e):
    return (
        render_template("error.html", error_message="Unauthorized", error_code=401),
        401,
    )


@bp.errorhandler(403)
def forbidden(e):
    return (
        render_template("error.html", error_message="Forbidden", error_code=403),
        403,
    )


@bp.errorhandler(500)
def internal_server_error(e):
    return (
        render_template(
            "error.html", error_message="Internal server error", error_code=500
        ),
        500,
    )

@bp.route('/process_evaluation', methods=['POST'])
def process_evaluation():
    if request.method != "POST":
        return render_template("index.html")

    if 'reference_file' not in request.files or 'test_file' not in request.files:
        return abort(400)

    reference_file = request.files['reference_file']
    test_file = request.files['test_file']

    model = request.form.get("model")
    if not model:
        return abort(400)

    api_key = request.form.get("api_key")
    if not api_key:
        return abort(400)

    custom_prompt = request.form.get("custom_prompt", "").strip() 
    client = AIClientFactory.create_client(model, api_key)
    file_processer = current_app.extensions["file_processer"]
    diff_generator = current_app.extensions["diff_generator"]

    ref_file = file_processer.validate_file(reference_file)
    filepath, filename = file_processer.save_file(ref_file)
    reference_lines, content = file_processer.read_txt_paragraphs(filepath)
    
    test_files = file_processer.process(test_file, client, model, custom_prompt if custom_prompt else None)

    diff_trans = diff_generator.generate_diff(
        reference_lines,
        test_files["input_file"]["paragraphs"]
    )

    diff_corr = diff_generator.generate_diff(
        reference_lines,
        test_files["output_file"]["paragraphs"]
    )

    trans_lines = test_files["input_file"]["paragraphs"]
    corr_lines = test_files["output_file"]["paragraphs"]

    results_metrics = []
    for idx, (ref_line, corr_line, trans_line) in enumerate(zip(reference_lines, corr_lines, trans_lines), start=1):
        ref_line_clean = ref_line.strip()
        corr_line_clean = corr_line.strip()
        trans_line_clean = trans_line.strip()
        if not ref_line_clean or not corr_line_clean or not trans_line_clean:
            continue
        try:
            bleu_original = calculate_bleu(ref_line_clean, trans_line_clean)
            bert_original = calculate_bert_score(ref_line_clean, trans_line_clean)

            bleu_corrected = calculate_bleu(ref_line_clean, corr_line_clean)
            bert_corrected = calculate_bert_score(ref_line_clean, corr_line_clean)

            results_metrics.append({
                'index': idx,
                'bleu_original': round(bleu_original * 100, 1),
                'bleu_corrected': round(bleu_corrected * 100, 1),
                'bleu_diff': round((bleu_corrected - bleu_original) * 100, 1),
                'bert_original': round(bert_original * 100, 1),
                'bert_corrected': round(bert_corrected * 100, 1),
                'bert_diff': round((bert_corrected - bert_original) * 100, 1),
            })
        except Exception:
            results_metrics.append({
                'index': idx,
                'bleu_original': 0,
                'bleu_corrected': 0,
                'bleu_diff': 0,
                'bert_original': 0,
                'bert_corrected': 0,
                'bert_diff': 0,
            })

    return render_template(
        "evaluation.html",
        trans_redlines=diff_trans,
        corr_redlines=diff_corr,
        reference_lines=reference_lines,
        metrics=results_metrics
    )

@bp.route('/demo', methods=['GET'])
def demo():
    demo_dir = os.path.join(current_app.root_path, 'demo_data')
    reference_path = os.path.join(demo_dir, 'reference.txt')
    transcription_path = os.path.join(demo_dir, 'transcription.txt')
    corrected_path = os.path.join(demo_dir, 'corrected.txt')
    json_path = os.path.join(demo_dir, 'results_metrics.json')
    
    def read_demo_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    
    demo_data = {
        'reference_lines': read_demo_file(reference_path),
        'transcription_lines': read_demo_file(transcription_path),
        'corrected_lines': read_demo_file(corrected_path)
    }
    
    min_length = min(len(demo_data['reference_lines']), 
                    len(demo_data['transcription_lines']), 
                    len(demo_data['corrected_lines']))
    
    demo_data['reference_lines'] = demo_data['reference_lines'][:min_length]
    demo_data['transcription_lines'] = demo_data['transcription_lines'][:min_length]
    demo_data['corrected_lines'] = demo_data['corrected_lines'][:min_length]
    
    diff_generator = current_app.extensions["diff_generator"]
    
    diff_trans = diff_generator.generate_diff(
        demo_data['reference_lines'],
        demo_data['transcription_lines']
    )

    diff_corr = diff_generator.generate_diff(
        demo_data['reference_lines'],
        demo_data['corrected_lines']
    )

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            results_metrics = json.load(f)
    except FileNotFoundError:
        results_metrics = []
        print("Arquivo result_metrics.json não encontrado")
    except Exception as e:
        results_metrics = []
        print(f"Erro ao carregar JSON: {e}")

    return render_template(
        "evaluation.html",
        trans_redlines=diff_trans,
        corr_redlines=diff_corr,
        reference_lines=demo_data['reference_lines'],
        metrics=results_metrics,
        is_demo=True
    )