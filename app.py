from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.main import bp as main_bp
from ext.file_processer import FileProcesser
from ext.diff_generator import DiffGenerator

app = Flask(__name__)

file_processer = FileProcesser()
diff_generator = DiffGenerator()

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

file_processer.init_app(app)
diff_generator.init_app(app)

app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
