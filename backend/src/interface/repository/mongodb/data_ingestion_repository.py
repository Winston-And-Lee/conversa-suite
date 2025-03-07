from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from src.domain.models.data_ingestion import DataIngestion, DataType


class DataIngestionRepository:
    """Repository for data ingestion using MongoDB."""

    def __init__(self, database):
        """Initialize the repository with a MongoDB database connection."""
        self.collection = database["data_ingestion"]

    async def create(self, data_ingestion: DataIngestion) -> DataIngestion:
        """Create a new data ingestion entry."""
        # Convert DataIngestion model to dictionary
        data_dict = data_ingestion.dict(exclude={"id"})
        
        # Convert enum to string for MongoDB storage
        if isinstance(data_dict.get("data_type"), DataType):
            data_dict["data_type"] = data_dict["data_type"].value
        
        # Set timestamps
        now = datetime.utcnow()
        data_dict["created_at"] = now
        data_dict["updated_at"] = now
        
        # Insert into MongoDB
        result = await self.collection.insert_one(data_dict)
        
        # Set the ID on the DataIngestion object
        data_ingestion.id = str(result.inserted_id)
        
        return data_ingestion
    
    async def get_by_id(self, id: str) -> Optional[DataIngestion]:
        """Get data ingestion by ID."""
        result = await self.collection.find_one({"_id": ObjectId(id)})
        
        if not result:
            return None
        
        # Convert MongoDB document to DataIngestion
        result["id"] = str(result.pop("_id"))
        return DataIngestion(**result)
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[DataIngestion]:
        """Update data ingestion."""
        # Set updated timestamp
        data["updated_at"] = datetime.utcnow()
        
        # Convert enum to string if present
        if "data_type" in data and isinstance(data["data_type"], DataType):
            data["data_type"] = data["data_type"].value
        
        # Update document in MongoDB
        result = await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        
        if result.modified_count == 0:
            return None
        
        # Get updated document
        return await self.get_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """Delete data ingestion."""
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def get_all(self, limit: int = 100, skip: int = 0) -> List[DataIngestion]:
        """Get all data ingestion entries with pagination."""
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        result = []
        
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            result.append(DataIngestion(**document))
        
        return result
    
    async def get_by_pinecone_id(self, pinecone_id: str) -> Optional[DataIngestion]:
        """Get data ingestion by Pinecone ID."""
        result = await self.collection.find_one({"pinecone_id": pinecone_id})
        
        if not result:
            return None
        
        result["id"] = str(result.pop("_id"))
        return DataIngestion(**result) 