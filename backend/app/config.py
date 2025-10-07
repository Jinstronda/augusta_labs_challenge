"""
Configuration management for the backend API

Loads environment variables and provides typed configuration settings.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Get the project root directory (parent of backend/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(project_root, 'config.env')

# Load environment variables from config.env
load_dotenv(config_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database configuration
    DB_NAME: str = os.getenv("DB_NAME", "incentives_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Seneca138$$")  # Default password
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    
    # Qdrant configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "companies")
    
    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPEN_AI", "")
    
    # Model configuration
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    
    # API configuration
    API_TIMEOUT: int = 30
    MAX_RESULTS: int = 5
    
    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Alternative Vite port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        env_file = "config.env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment


# Create global settings instance
settings = Settings()
