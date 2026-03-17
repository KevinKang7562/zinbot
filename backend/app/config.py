from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / "backend" / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")

    llm_api_base: str = Field(default="http://localhost:1234", alias="LLM_API_BASE")
    llm_chat_api_url: str = Field(
        default="https://openrouter.ai/api/v1/chat/completions",
        alias="LLM_CHAT_API_URL",
    )
    llm_api_key: str = Field(
        default="",
        alias="LLM_API_KEY",
    )
    embedding_api_url: str = Field(
        default="https://openrouter.ai/api/v1/embeddings",
        alias="EMBEDDING_API_URL",
    )
    embedding_api_key: str = Field(
        default="",
        alias="EMBEDDING_API_KEY",
    )
    embedding_model: str = Field(default="intfloat/multilingual-e5-large", alias="EMBEDDING_MODEL")
    llm_model: str = Field(default="google/gemma-3-27b-it:scaleway", alias="LLM_MODEL")

    qdrant_url: str = Field(
        default="http://localhost:6333",
        alias="QDRANT_URL",
    )
    qdrant_api_key: str = Field(
        default="",
        alias="QDRANT_API_KEY",
    )
    qdrant_collection: str = Field(default="company_docs", alias="QDRANT_COLLECTION")
    score_threshold: float = Field(default=0.7, alias="SCORE_THRESHOLD")

    allowed_origins: list[str] = ["*"]


settings = Settings()
