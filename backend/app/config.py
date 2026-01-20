"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    
    # Default LLM Provider
    default_llm_provider: Literal["openai", "ollama"] = "openai"
    
    # Default Models
    default_openai_model: str = "gpt-4"
    default_ollama_model: str = "llama3"
    
    # Vector Store Configuration
    vector_store_path: str = "./vector_store"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Retrieval Configuration
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.3
    
    # Chunking Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Upload Configuration
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list[str] = ["pdf", "txt", "docx"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
