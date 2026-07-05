from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    YOUTUBE_API_KEY: Optional[str] = None
    
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Enable loading from .env file located at the root of the project
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../../.env"), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
