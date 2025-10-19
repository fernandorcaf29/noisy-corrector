import sys
import os
from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.main import bp as main_bp
from ext.file_processor import FileProcessor
from ext.diff_generator import DiffGenerator

if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')  # Windows UTF-8
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

app = Flask(__name__)

file_processor = FileProcessor()
diff_generator = DiffGenerator()

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

file_processor.init_app(app)
diff_generator.init_app(app)

app.register_blueprint(main_bp)
