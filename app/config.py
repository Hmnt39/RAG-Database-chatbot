"""Application settings and configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="rag_chatbot", alias="MONGODB_DB_NAME")

    # OpenAI Configuration
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    embedding_mode: str = Field(default="local", alias="EMBEDDING_MODE")

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    # Application Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_history: int = Field(default=10, alias="MAX_HISTORY")
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __repr__(self) -> str:
        return f"Settings(mongodb_uri={self.mongodb_uri}, db_name={self.mongodb_db_name})"
