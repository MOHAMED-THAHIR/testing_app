import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/testa_uploads")
    ALLOWED_EXTENSIONS = {
        "py", "js", "ts", "jsx", "tsx", "vue", "html", "css", "scss",
        "java", "cs", "go", "rb", "php", "swift", "kt", "rs", "cpp",
        "c", "h", "json", "yaml", "yml", "xml", "zip", "tar", "gz"
    }
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    SECRET_KEY = os.getenv("SECRET_KEY", "testa-dev-secret-key-change-in-prod")
    VERSION = "1.0.0"
    APP_NAME = "Testa"