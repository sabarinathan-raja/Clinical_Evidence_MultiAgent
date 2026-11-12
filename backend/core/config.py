
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    APP_NAME: str = "Clinical Evidence Multi-Agent AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    SECRET_KEY: str = Field(
        default="development-only-change-this-secret"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    DATABASE_URL: str = "sqlite:///./clinical_evidence.db"

    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "clinical_evidence"

    EMBEDDING_MODEL: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    RERANKER_MODEL: str = (
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    TOP_K: int = 5
    RERANK_TOP_K: int = 3

    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: str = "pdf,txt,md"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/application.log"

    ENABLE_AUTH: bool = True
    ENABLE_HUMAN_REVIEW: bool = True
    ENABLE_AUDIT_LOG: bool = True

    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def allowed_extensions_list(self):
        return [
            item.strip().lower()
            for item in self.ALLOWED_EXTENSIONS.split(",")
            if item.strip()
        ]

    @property
    def cors_origins_list(self):
        return [
            item.strip()
            for item in self.CORS_ORIGINS.split(",")
            if item.strip()
        ]

    @property
    def chroma_path(self):
        path = Path(self.CHROMA_PERSIST_DIRECTORY)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @property
    def database_path(self):
        return ROOT_DIR


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
