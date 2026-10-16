import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-calorie-key-change-in-production")
    
    # Database config with SQLite fallback if Postgres is not configured
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        db_path = BASE_DIR / "calorie_app.db"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-super-secret-key-nutrition-agent")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Upload configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # LLM Provider configuration: 'gemini' or 'ollama'
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

    # Gemini LLM configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-flash-lite-latest")

    # Local Ollama configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

    AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-32-bytes-long-super-safe-nutri"


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
