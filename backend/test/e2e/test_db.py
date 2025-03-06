"""Test database setup and teardown."""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure.database.mongodb import MongoDB


@pytest.fixture(scope="session")
async def test_db():
    """Set up and tear down the test database."""
    # Connect to the test database
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.conversa_test
    
    # Override the MongoDB singleton for testing
    MongoDB._db = db
    
    # Clear the database before tests
    await clear_db(db)
    
    yield db
    
    # Clear the database after tests
    await clear_db(db)


async def clear_db(db):
    """Clear all collections in the database."""
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})


@pytest.fixture(autouse=True)
async def setup_test_db(test_db):
    """Set up the test database before each test."""
    # Clear the database before each test
    await clear_db(test_db)
    
    yield
    
    # No need to clear after each test as we're using a clean database for each test 