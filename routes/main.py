from flask import Blueprint, render_template, request, abort, current_app
from aiClients.ai_client_factory import AIClientFactory
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
    print("diff", diff)
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

    client = AIClientFactory.create_client(model, api_key)
    file_processer = current_app.extensions["file_processer"]
    diff_generator = current_app.extensions["diff_generator"]

    ref_files = file_processer.process(reference_file, client, model)
    test_files = file_processer.process(test_file, client, model)

    diff = diff_generator.generate_diff(
        ref_files["output_file"]["paragraphs"],
        test_files["output_file"]["paragraphs"]
    )

    reference_lines = ref_files["output_file"]["paragraphs"]
    test_lines = test_files["output_file"]["paragraphs"]

    results_metrics = []
    for idx, (ref_line, test_line) in enumerate(zip(reference_lines, test_lines), start=1):
        ref_line_clean = ref_line.strip()
        test_line_clean = test_line.strip()
        if not ref_line_clean or not test_line_clean:
            continue
        try:
            bleu_original = calculate_bleu(ref_line_clean, ref_line_clean)
            bert_original = calculate_bert_score(ref_line_clean, ref_line_clean)

            bleu_corrected = calculate_bleu(ref_line_clean, test_line_clean)
            bert_corrected = calculate_bert_score(ref_line_clean, test_line_clean)

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
        redlines=diff,
        reference_lines=reference_lines,
        file_content=test_files["output_file"]["content"],
        filename=test_files["output_file"]["filename"],
        metrics=results_metrics
    )
