from flask import Blueprint, render_template, request, abort, current_app
from aiClients.ai_client_factory import AIClientFactory

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