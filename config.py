import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Use a persistent secret key from .env, or a fallback for development
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-12345")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/careerverse")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email settings
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # Security for tokens
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "my_precious_salt")

    # Default settings
    DEFAULT_SETTINGS = {
        "ai_style": "Standard",
        "ocr_mode": "Balanced",
        "chat_enabled": True,
        "voice_enabled": False,
        "voice_type": "nova",
        "language": "English",
        "response_font_size": 16,
    }
