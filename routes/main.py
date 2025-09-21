from flask import Blueprint, render_template, request, abort, current_app
from aiClients.ai_client_factory import AIClientFactory

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


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
