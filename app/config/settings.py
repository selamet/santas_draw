"""
Application configuration settings
Loads environment variables from .env file
"""

from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = "Santa's Draw API"
    app_version: str = "1.0.0"
    debug: bool = True
    api_version: str = "v1"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/santas_draw"
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()
