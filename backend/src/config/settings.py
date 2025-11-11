"""Application configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET", "default-secret-key")
    TESTING = False
    DEBUG = False
    MAX_CONTENT_LENGTH = int(float(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024)
    
    # Model settings
    EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    # Search settings
    USE_HYBRID = os.getenv("USE_HYBRID", "false").lower() in {"1", "true", "yes", "on"}
    USE_RERANKER = os.getenv("USE_RERANKER", "false").lower() in {"1", "true", "yes", "on"}
    TOP_K = 5
    CANDIDATES = 20
    FUSE_ALPHA = 0.5
    MIN_HYBRID = 0.1
    AVG_HYBRID = 0.1
    MIN_SEM_SIM = 0.35
    AVG_SEM_SIM = 0.2
    MIN_RERANK = 0.5
    AVG_RERANK = 0.3
    
    # Document processing
    SENT_TARGET = 400
    SENT_OVERLAP = 90
    TEXT_MAX = 400000
    
    # Chat settings
    CHAT_MAX_TOKENS = 200
    MAX_HISTORY = 3
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Database
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
    
    # File upload
    UPLOAD_BASE = os.getenv("UPLOAD_BASE", "uploads")
    MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "25"))
    ALLOWED_EXTENSIONS = ["txt", "pdf", "docx", "md"]
    MIME_TYPES = [
        "text/plain",
        "text/markdown",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument"
    ]
    FOLDER_SHARED = "shared"
    DEPT_SPLIT = "|"
    
    # Auth
    SERVICE_AUTH_SECRET = os.getenv("SERVICE_AUTH_SECRET", "")
    SERVICE_AUTH_ISSUER = os.getenv("SERVICE_AUTH_ISSUER", "your_service_name")
    SERVICE_AUTH_AUDIENCE = os.getenv("SERVICE_AUTH_AUDIENCE", "your_service_audience")
    
    # Organization
    ORG_STRUCTURE_FILE = os.getenv("ORG_STRUCTURE_FILE", "org_structure.json")
    
    # Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    DEFAULT_RATE_LIMITS = ["500 per day", "20 per minute"]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MAX_CONTENT_LENGTH = int(float(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024)


class ProductionConfig(Config):
    """Production configuration"""
    pass


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
