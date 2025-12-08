"""
Configuration management for the backend application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Multilingual AI Intelligence Platform"
    VERSION: str = "1.0.0"
    
    # Groq LLM Settings
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 2048
    
    # Embeddings Settings (using transformers library)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"  # "cpu" or "cuda"
    
    # Qdrant Settings
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "multilingual_docs"
    
    # RAG Settings
    RAG_TOP_K: int = 4
    RAG_MIN_SCORE: float = 0.2  # Lower threshold to get more relevant results
    
    # ML Model Settings
    SENTIMENT_MODEL_PATH: str = "./app/models/sentiment_model.pkl"
    
    # Document Processing
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SUPPORTED_FILE_TYPES: list = [".pdf", ".txt", ".csv"]
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

