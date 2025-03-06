"""Mock settings for tests."""
import pytest
from typing import List


class MockSettings:
    """Mock settings class for tests."""
    
    APP_NAME: str = "Conversa-Suite Test"
    DEBUG: bool = True
    HOST: str = "localhost"
    PORT: int = 8000
    MONGODB_URI: str = "mongodb://localhost:27017/conversa_test"
    ALLOWED_ORIGINS: List[str] = ["*"]


def get_settings():
    """Get mock settings."""
    return MockSettings()


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock settings for all tests."""
    monkeypatch.setattr("src.config.settings.get_settings", get_settings)
    return get_settings() 