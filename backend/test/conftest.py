"""Test configuration for pytest."""
import os
import pytest
import asyncio
from typing import Generator

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/conversa_test"
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 