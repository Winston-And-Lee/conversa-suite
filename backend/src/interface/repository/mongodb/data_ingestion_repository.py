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
    
    async def find_all(self, skip: int = 0, limit: int = 10, sort: Optional[Dict[str, int]] = None) -> List[DataIngestion]:
        """
        Find all data ingestion entries with pagination and optional sorting.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: Dictionary of field names and sort directions (1 for ascending, -1 for descending)
            
        Returns:
            List[DataIngestion]: List of data ingestion items
        """
        # Create a cursor with pagination
        cursor = self.collection.find()
        
        # Apply sorting if provided
        if sort:
            sort_list = []
            for field, direction in sort.items():
                sort_list.append((field, direction))
            cursor = cursor.sort(sort_list)
        else:
            # Default sort by created_at descending
            cursor = cursor.sort("created_at", -1)
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        # Convert documents to DataIngestion objects
        result = []
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            result.append(DataIngestion(**document))
        
        return result
    
    async def find_by_criteria(self, criteria: Dict[str, Any], skip: int = 0, limit: int = 10, sort: Optional[Dict[str, int]] = None) -> List[DataIngestion]:
        """
        Find data ingestion entries by criteria with pagination and optional sorting.
        
        Args:
            criteria: Dictionary of field names and values to filter by
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: Dictionary of field names and sort directions (1 for ascending, -1 for descending)
            
        Returns:
            List[DataIngestion]: List of data ingestion items matching the criteria
        """
        # Create a cursor with the filter criteria
        cursor = self.collection.find(criteria)
        
        # Apply sorting if provided
        if sort:
            sort_list = []
            for field, direction in sort.items():
                sort_list.append((field, direction))
            cursor = cursor.sort(sort_list)
        else:
            # Default sort by created_at descending
            cursor = cursor.sort("created_at", -1)
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        # Convert documents to DataIngestion objects
        result = []
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            result.append(DataIngestion(**document))
        
        return result
    
    async def find_by_id(self, id: str) -> Optional[DataIngestion]:
        """
        Find data ingestion by ID.
        
        Args:
            id: MongoDB ID
            
        Returns:
            Optional[DataIngestion]: Data ingestion item if found, None otherwise
        """
        return await self.get_by_id(id)
    
    async def count(self) -> int:
        """
        Count all data ingestion entries.
        
        Returns:
            int: Total count of data ingestion items
        """
        return await self.collection.count_documents({})
    
    async def count_by_criteria(self, criteria: Dict[str, Any]) -> int:
        """
        Count data ingestion entries matching the criteria.
        
        Args:
            criteria: Dictionary of field names and values to filter by
            
        Returns:
            int: Count of data ingestion items matching the criteria
        """
        return await self.collection.count_documents(criteria) 