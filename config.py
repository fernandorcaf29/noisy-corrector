import os

UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'json', 'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)