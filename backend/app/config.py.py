from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Usage:
        from app.config import settings
        api_key = settings.ANTHROPIC_API_KEY
    """
    
    # API Configuration
    API_TITLE: str = "SafeGuard AI"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Multi-layer prompt injection detection system"
    ANTHROPIC_API_KEY: str  
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["*"] 
    
    # Rate Limiting
    MAX_PROMPT_LENGTH: int = 10000  # Characters
    
    # Claude Configuration
    CLAUDE_MODEL: str = "claude-3-haiku-20240307"
    CLAUDE_MAX_TOKENS: int = 512
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"  # Load from .env file
        case_sensitive = True  # ANTHROPIC_API_KEY != anthropic_api_key

@lru_cache()  # Cache the settings 
def get_settings() -> Settings:
    return Settings()

# Export a single settings instance
settings = get_settings()