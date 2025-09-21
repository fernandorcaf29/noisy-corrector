from flask import Blueprint, render_template, request, abort, current_app
from aiClients.ai_client_factory import AIClientFactory

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@bp.route("/result", methods=["POST"])
def result():
    if "document" not in request.files:
        return abort(400)

    file = request.files["document"]

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
