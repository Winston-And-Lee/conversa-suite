import logging
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
from datetime import datetime

from src.domain.models.file import FileResource, FileType

logger = logging.getLogger(__name__)

class FileResourceRepository:
    """Repository for file resources in MongoDB"""
    
    def __init__(self, db):
        """Initialize with MongoDB database instance"""
        self.db = db
        self.collection = db["file_resources"]
    
    async def create(self, file_resource: FileResource) -> FileResource:
        """
        Create a new file resource
        
        Args:
            file_resource: FileResource object to create
            
        Returns:
            Created FileResource with ID
        """
        try:
            # Convert to dict for MongoDB
            file_dict = file_resource.model_dump(by_alias=True)
            
            # Remove _id if it's None
            if "_id" in file_dict and file_dict["_id"] is None:
                del file_dict["_id"]
            
            # Insert into MongoDB
            result = await self.collection.insert_one(file_dict)
            
            # Update the ID in the model
            file_resource.id = str(result.inserted_id)
            
            logger.info(f"Created file resource with ID: {file_resource.id}")
            return file_resource
        except Exception as e:
            logger.error(f"Error creating file resource: {str(e)}")
            raise
    
    async def find_by_id(self, id: str) -> Optional[FileResource]:
        """
        Find a file resource by ID
        
        Args:
            id: File resource ID
            
        Returns:
            FileResource if found, None otherwise
        """
        try:
            result = await self.collection.find_one({"_id": ObjectId(id)})
            if result:
                # Convert MongoDB document to FileResource
                result["id"] = str(result["_id"])
                return FileResource.model_validate(result)
            return None
        except Exception as e:
            logger.error(f"Error finding file resource by ID: {str(e)}")
            raise
    
    async def find(self, filter_params: Dict[str, Any], limit: int = 10, offset: int = 0, sort: List[Tuple[str, int]] = None) -> List[FileResource]:
        """
        Find file resources by filter parameters
        
        Args:
            filter_params: Filter parameters
            limit: Maximum number of results
            offset: Number of results to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List of FileResource objects
        """
        try:
            cursor = self.collection.find(filter_params)
            
            # Apply sorting if provided
            if sort:
                cursor = cursor.sort(sort)
            
            # Apply pagination
            cursor = cursor.skip(offset).limit(limit)
            
            # Convert results to FileResource objects
            results = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                results.append(FileResource.model_validate(doc))
            
            return results
        except Exception as e:
            logger.error(f"Error finding file resources: {str(e)}")
            raise
    
    async def count(self, filter_params: Dict[str, Any]) -> int:
        """
        Count file resources by filter parameters
        
        Args:
            filter_params: Filter parameters
            
        Returns:
            Count of matching file resources
        """
        try:
            return await self.collection.count_documents(filter_params)
        except Exception as e:
            logger.error(f"Error counting file resources: {str(e)}")
            raise
    
    async def update(self, id: str, update_data: Dict[str, Any]) -> Optional[FileResource]:
        """
        Update a file resource
        
        Args:
            id: File resource ID
            update_data: Data to update
            
        Returns:
            Updated FileResource if found, None otherwise
        """
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update in MongoDB
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                # Convert MongoDB document to FileResource
                result["id"] = str(result["_id"])
                return FileResource.model_validate(result)
            return None
        except Exception as e:
            logger.error(f"Error updating file resource: {str(e)}")
            raise
    
    async def delete(self, id: str) -> bool:
        """
        Delete a file resource
        
        Args:
            id: File resource ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting file resource: {str(e)}")
            raise
    
    async def delete_by_filter(self, filter_params: Dict[str, Any]) -> int:
        """
        Delete file resources by filter parameters
        
        Args:
            filter_params: Filter parameters
            
        Returns:
            Number of deleted file resources
        """
        try:
            result = await self.collection.delete_many(filter_params)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting file resources by filter: {str(e)}")
            raise 