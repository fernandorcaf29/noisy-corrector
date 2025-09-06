from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.main import bp as main_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)