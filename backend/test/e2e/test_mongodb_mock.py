"""MongoDB mock for e2e tests."""
import pytest
import uuid
from typing import Dict, List, Any, Optional
from bson import ObjectId
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.domain.models.user import User
from src.interface.repository.mongodb.user_repository import MongoDBUserRepository


class MockCursor:
    """Mock cursor for MongoDB queries."""
    
    def __init__(self, items):
        self.items = items
        self.current_index = 0
        
    def __aiter__(self):
        return self
        
    async def __anext__(self):
        if self.current_index < len(self.items):
            item = self.items[self.current_index]
            self.current_index += 1
            return item
        raise StopAsyncIteration


class MockCollection:
    """Mock MongoDB collection."""
    
    def __init__(self, name="users"):
        self.name = name
        self.data = []
        self.next_id = 1
        
    async def insert_one(self, document):
        """Insert a document into the collection."""
        # Add _id field if not present
        if "_id" not in document:
            document["_id"] = ObjectId()
        
        self.data.append(document)
        result = MagicMock()
        result.inserted_id = document["_id"]
        return result
        
    async def find_one(self, query):
        """Find a single document matching the query."""
        for doc in self.data:
            if self._matches_query(doc, query):
                # Return a copy to prevent modifying the original
                return doc.copy()
        return None
        
    async def find(self, query=None):
        """Find documents matching the query."""
        if query is None:
            query = {}
            
        results = []
        for doc in self.data:
            if self._matches_query(doc, query):
                results.append(doc.copy())
        
        return MockCursor(results)
        
    async def update_one(self, query, update):
        """Update a single document matching the query."""
        for i, doc in enumerate(self.data):
            if self._matches_query(doc, query):
                # Handle $set operation
                if "$set" in update:
                    for key, value in update["$set"].items():
                        doc[key] = value
                
                # Handle $push operation
                if "$push" in update:
                    for key, value in update["$push"].items():
                        if key not in doc:
                            doc[key] = []
                        doc[key].append(value)
                
                # Handle $pull operation
                if "$pull" in update:
                    for key, value in update["$pull"].items():
                        if key in doc and isinstance(doc[key], list):
                            if value in doc[key]:
                                doc[key].remove(value)
                
                result = MagicMock()
                result.modified_count = 1
                return result
        
        result = MagicMock()
        result.modified_count = 0
        return result
        
    async def delete_one(self, query):
        """Delete a single document matching the query."""
        for i, doc in enumerate(self.data):
            if self._matches_query(doc, query):
                self.data.pop(i)
                result = MagicMock()
                result.deleted_count = 1
                return result
        
        result = MagicMock()
        result.deleted_count = 0
        return result
        
    async def delete_many(self, query):
        """Delete all documents matching the query."""
        deleted = 0
        i = 0
        while i < len(self.data):
            if self._matches_query(self.data[i], query):
                self.data.pop(i)
                deleted += 1
            else:
                i += 1
        
        result = MagicMock()
        result.deleted_count = deleted
        return result
        
    def _matches_query(self, doc, query):
        """Check if a document matches a query."""
        for key, value in query.items():
            # Handle special query operators
            if isinstance(value, dict) and "$regex" in value:
                # Simple regex support
                import re
                if key not in doc or not re.search(value["$regex"], doc[key]):
                    return False
            elif key == "_id" and isinstance(value, ObjectId):
                # Handle ObjectId comparison
                if key not in doc or doc[key] != value:
                    return False
            elif key not in doc or doc[key] != value:
                return False
        return True


class MockDatabase:
    """Mock MongoDB database."""
    
    def __init__(self):
        self.users = MockCollection("users")
        self.collections = {"users": self.users}
        
    def __getattr__(self, name):
        """Get a collection by name."""
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]


class MockMongoDB:
    """Mock MongoDB client."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockMongoDB, cls).__new__(cls)
            cls._instance.db = MockDatabase()
        return cls._instance
    
    def get_db(self):
        """Get the database object."""
        return self.db
        
    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        cls._instance = None


@pytest.fixture
def mock_mongodb(monkeypatch):
    """Mock MongoDB for testing."""
    # Reset the singleton instance
    MockMongoDB.reset()
    
    # Patch the MongoDB class
    with patch('src.infrastructure.database.mongodb.MongoDB', MockMongoDB):
        # Also patch any direct imports of MongoDB
        with patch('src.interface.repository.mongodb.user_repository.MongoDB', MockMongoDB):
            yield MockMongoDB() 