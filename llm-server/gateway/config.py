"""
Configuration for the LLM Gateway.
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings."""
    
    # Ollama configuration
    ollama_base_url: str = "http://ollama:11434"
    
    # API configuration
    api_key: str = "default-key-change-in-production"
    cors_origins: List[str] = ["*"]
    
    # Redis configuration
    redis_url: str = "redis://redis:6379"
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout: float = 120.0
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()