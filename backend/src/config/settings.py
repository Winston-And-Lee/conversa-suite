from functools import lru_cache
from typing import List, Union, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "backend-service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "debug"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MongoDB settings
    MONGO_URI: str
    MONGO_DB: str = "backend_db"
    MONGO_USER: str = ""
    MONGO_PASSWORD: str = ""

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # LangGraph settings
    LANGGRAPH_ASSISTANT_ID: str = "default_assistant"
    
    # LangChain tracing settings
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = ""
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings():
    """
    Get application settings with caching to improve performance.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    settings = Settings()
    # Log the MongoDB connection settings to help with debugging
    logger.info(f"MongoDB URI: {settings.MONGO_URI}")
    logger.info(f"MongoDB Database: {settings.MONGO_DB}")
    
    # Log LangChain tracing settings
    if settings.LANGCHAIN_API_KEY:
        logger.info(f"LangChain tracing enabled for project: {settings.LANGCHAIN_PROJECT}")
    
    return settings 