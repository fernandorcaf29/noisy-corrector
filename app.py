from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.main import bp as main_bp
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

class ProgressFilter(logging.Filter):
    def filter(self, record):
        return '/progress_status' not in record.getMessage()

# Aplicar o filter
log = logging.getLogger('werkzeug')
log.addFilter(ProgressFilter())

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)