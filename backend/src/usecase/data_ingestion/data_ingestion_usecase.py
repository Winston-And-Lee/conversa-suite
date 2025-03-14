import logging
import os
import re
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from src.domain.models.data_ingestion import DataIngestion, DataType
from src.domain.models.user import User
from src.infrastructure.services.text_extraction_service import TextExtractionService
from src.interface.repository.database.db_repository import data_ingestion_repository, s3_repository, pinecone_repository


class DataIngestionUseCase:
    """Use case for handling data ingestion operations."""

    def __init__(self):
        """Initialize with required repositories and services."""
        # Get repositories through factory functions
        self.data_ingestion_repository = data_ingestion_repository()
        # self.s3_repository = s3_repository()
        self.pinecone_repository = pinecone_repository()
        
        # Initialize services
        self.text_extraction_service = TextExtractionService()
        self.logger = logging.getLogger(__name__)
    
    def _filter_none_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out None values from a dictionary.
        
        Args:
            data: Dictionary that may contain None values
            
        Returns:
            Dict[str, Any]: Dictionary with None values removed
        """
        return {k: v for k, v in data.items() if v is not None}
    
    async def submit_data_ingestion(
        self,
        data_ingestion: DataIngestion,
        file_url: Optional[str] = None,
        user: Optional[User] = None
    ) -> DataIngestion:
        """
        Submit data ingestion with JSON payload.
        
        Args:
            data_ingestion: DataIngestion object with all required fields
            file_url: Optional URL to a file (overrides data_ingestion.file_url if provided)
            user: User who is submitting the data
            
        Returns:
            DataIngestion: Created data ingestion with IDs
        """
        try:
            # Set user_id if user is provided
            if user:
                data_ingestion.user_id = str(user.id)
                self.logger.info(f"Setting user_id: {data_ingestion.user_id}")
            
            # Initialize file_text
            file_text = ""
            
            # Override file_url if provided as a parameter
            if file_url:
                self.logger.info(f"Using provided file URL: {file_url}")
                data_ingestion.file_url = file_url
                
                # Extract filename from URL
                file_name = file_url.split("/")[-1]
                data_ingestion.file_name = file_name
                
                # Determine file type from URL extension
                if "." in file_name:
                    file_extension = file_name.split(".")[-1].lower()
                    if file_extension in ["pdf", "doc", "docx", "txt"]:
                        data_ingestion.file_type = file_extension
            
            # Handle webpage_url if provided
            if data_ingestion.webpage_url and not data_ingestion.file_url:
                self.logger.info(f"Using provided webpage URL: {data_ingestion.webpage_url}")
                
                # Validate URL format
                if not re.match(r'^https?://', data_ingestion.webpage_url):
                    self.logger.error(f"Invalid URL format: {data_ingestion.webpage_url}")
                    raise ValueError(f"Invalid URL format: {data_ingestion.webpage_url}. URL must start with http:// or https://")
                
                # Use the reference field if it's empty
                if not data_ingestion.reference:
                    data_ingestion.reference = data_ingestion.webpage_url
            
            # If keywords are empty, generate them
            if not data_ingestion.keywords:
                # Combine title, specified_text, content, and file_text for keyword generation
                combined_text = f"{data_ingestion.title} {data_ingestion.specified_text} {data_ingestion.content or ''} {file_text}"
                generated_keywords = await self.pinecone_repository.generate_keywords(combined_text)
                data_ingestion.keywords = generated_keywords
            
            # Save to MongoDB
            created_data_ingestion = await self.data_ingestion_repository.create(data_ingestion)
            
            # Create metadata for Pinecone
            metadata = {
                "mongodb_id": created_data_ingestion.id,
                "title": data_ingestion.title,
                "specified_text": data_ingestion.specified_text,
                "data_type": data_ingestion.data_type,
                "content": data_ingestion.content,
                "reference": data_ingestion.reference,
                "has_file": bool(data_ingestion.file_url),
                "user_id": data_ingestion.user_id
            }
            
            # Add optional fields only if they are not None
            if data_ingestion.file_url:
                metadata["file_url"] = data_ingestion.file_url
            
            if data_ingestion.webpage_url:
                metadata["webpage_url"] = data_ingestion.webpage_url
            
            # Filter out any None values from metadata
            metadata = self._filter_none_values(metadata)
            
            # Create text data for embedding
            text_data = {
                "title": data_ingestion.title,
                "specified_text": data_ingestion.specified_text,
                "content": data_ingestion.content or "",
                "keywords": created_data_ingestion.keywords,
                "file_text": file_text
            }
            
            # Filter out any None values from text_data
            text_data = self._filter_none_values(text_data)
            
            # Store in Pinecone
            pinecone_id = None
            
            # If we have a file URL, load the file content into Pinecone
            if data_ingestion.file_url and data_ingestion.file_type in ["pdf", "doc", "docx", "txt"]:
                try:
                    # Load file from URL and store chunks in Pinecone
                    vector_ids = await self.pinecone_repository.load_file_from_url(data_ingestion.file_url, metadata)
                    
                    if vector_ids:
                        # Use the first vector ID as the main pinecone_id
                        pinecone_id = vector_ids[0]
                        self.logger.info(f"Loaded file from URL into Pinecone with {len(vector_ids)} chunks")
                except Exception as e:
                    self.logger.error(f"Error loading file from URL into Pinecone: {str(e)}")
                    # Continue with normal embedding if file loading fails
            
            # If we have a webpage URL, load the webpage content into Pinecone
            elif data_ingestion.webpage_url:
                try:
                    # Load webpage and store chunks in Pinecone
                    vector_ids = await self.pinecone_repository.load_webpage(data_ingestion.webpage_url, metadata)
                    
                    if vector_ids:
                        # Use the first vector ID as the main pinecone_id
                        pinecone_id = vector_ids[0]
                        self.logger.info(f"Loaded webpage from URL into Pinecone with {len(vector_ids)} chunks")
                except Exception as e:
                    self.logger.error(f"Error loading webpage from URL into Pinecone: {str(e)}")
                    # Continue with normal embedding if webpage loading fails
            
            # If we don't have a pinecone_id yet (file/webpage loading failed or wasn't attempted),
            # store the regular text data
            if not pinecone_id:
                pinecone_id = await self.pinecone_repository.upsert_vector(text_data, metadata)
            
            # Update DataIngestion with Pinecone ID
            await self.data_ingestion_repository.update(
                created_data_ingestion.id,
                {"pinecone_id": pinecone_id}
            )
            created_data_ingestion.pinecone_id = pinecone_id
            
            return created_data_ingestion
            
        except Exception as e:
            self.logger.error(f"Data ingestion submission error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data ingestion submission error: {str(e)}")
    
    async def get_data_ingestion(self, data_id: str, user: Optional[User] = None) -> DataIngestion:
        """
        Get data ingestion by ID.
        
        Args:
            data_id: Data ingestion ID
            user: User requesting the data
            
        Returns:
            DataIngestion: Retrieved data ingestion
        """
        data_ingestion = await self.data_ingestion_repository.get_by_id(data_id)
        
        if not data_ingestion:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        return data_ingestion
    
    async def search_data_ingestion(
        self, 
        query: str, 
        skip: int = 0,
        limit: int = 10,
        user: Optional[User] = None
    ) -> List[Dict[str, Any]]:
        """
        Search data ingestion using text query.
        
        Args:
            query: Text query to search for
            skip: Number of items to skip (for pagination)
            limit: Maximum number of results to return
            user: User performing the search
            
        Returns:
            List[Dict[str, Any]]: List of search results with similarity scores
        """
        try:
            if not query:
                # If no query provided, return all data with pagination
                data_items = await self.data_ingestion_repository.find_all(skip=skip, limit=limit)
                
                # Convert to dict format
                results = []
                for item in data_items:
                    item_dict = item.dict()
                    # Add a placeholder similarity score of 1.0 for sorting consistency
                    item_dict["similarity_score"] = 1.0
                    results.append(item_dict)
                    
                return results
            else:
                # Search in Pinecone
                search_results = await self.pinecone_repository.search(
                    query=query,
                    limit=limit,
                    offset=skip
                )
                
                # Get full data from MongoDB for each result
                results = []
                for result in search_results:
                    mongodb_id = result["id"]
                    data_item = await self.data_ingestion_repository.find_by_id(mongodb_id)
                    
                    if data_item:
                        # Convert to dict and add similarity score
                        item_dict = data_item.dict()
                        item_dict["similarity_score"] = result["similarity_score"]
                        results.append(item_dict)
                
                return results
        except Exception as e:
            self.logger.error(f"Error searching data ingestion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching data: {str(e)}")
    
    async def list_data_ingestion(
        self, 
        query: str = "", 
        data_type: Optional[str] = None,
        keywords: Optional[str] = None,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        user: Optional[User] = None
    ) -> List[DataIngestion]:
        """
        List data ingestion items with optional filtering, pagination, and sorting.
        
        Args:
            query: Optional text query to filter by
            data_type: Optional data type to filter by
            keywords: Optional keywords to filter by
            title: Optional title to filter by
            skip: Number of items to skip (for pagination)
            limit: Maximum number of results to return
            sort_field: Field to sort by
            sort_order: Sort order (asc or desc)
            user: User performing the search
            
        Returns:
            List[DataIngestion]: List of data ingestion items
        """
        try:
            # Prepare sort parameters
            sort_params = None
            if sort_field:
                # Convert sort order to 1 (ascending) or -1 (descending)
                sort_direction = -1 if sort_order and sort_order.lower() == 'desc' else 1
                sort_params = {sort_field: sort_direction}
            
            # Build filter criteria
            filter_criteria = {}
            if data_type:
                filter_criteria["data_type"] = data_type
            
            # Add keywords filter if provided
            if keywords:
                # Use regex to search for keywords that contain the provided string
                filter_criteria["keywords"] = {"$regex": keywords, "$options": "i"}
            
            # Add title filter if provided
            if title:
                # Use regex to search for title containing the provided string
                filter_criteria["title"] = {"$regex": title, "$options": "i"}
            
            if not query and (data_type or keywords or title):
                # If only filter criteria are provided (no full-text search)
                data_items = await self.data_ingestion_repository.find_by_criteria(
                    criteria=filter_criteria,
                    skip=skip,
                    limit=limit,
                    sort=sort_params
                )
                return data_items
            elif not query:
                # If no filters provided, return all data with pagination and sorting
                data_items = await self.data_ingestion_repository.find_all(
                    skip=skip, 
                    limit=limit,
                    sort=sort_params
                )
                return data_items
            else:
                # Search in Pinecone with query
                search_results = await self.pinecone_repository.search(
                    query=query,
                    limit=limit,
                    offset=skip
                )
                
                # Get full data from MongoDB for each result
                results = []
                for result in search_results:
                    mongodb_id = result["id"]
                    data_item = await self.data_ingestion_repository.find_by_id(mongodb_id)
                    
                    # Apply filters if provided
                    if data_item:
                        if data_type and data_item.data_type != data_type:
                            continue
                        
                        if keywords and not any(keywords.lower() in keyword.lower() for keyword in data_item.keywords):
                            continue
                        
                        if title and title.lower() not in data_item.title.lower():
                            continue
                        
                        results.append(data_item)
                
                # For Pinecone results, we can't easily apply MongoDB sorting
                # We could implement manual sorting here if needed
                
                return results
        except Exception as e:
            self.logger.error(f"Error listing data ingestion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing data: {str(e)}")
    
    async def count_data_ingestion(
        self, 
        query: str = "", 
        data_type: Optional[str] = None, 
        keywords: Optional[str] = None,
        title: Optional[str] = None,
        user: Optional[User] = None
    ) -> int:
        """
        Count total data ingestion items, optionally filtered by query, data_type, keywords, and title.
        
        Args:
            query: Optional text query to filter by
            data_type: Optional data type to filter by
            keywords: Optional keywords to filter by
            title: Optional title to filter by
            user: User performing the count
            
        Returns:
            int: Total count of matching items
        """
        try:
            # Build filter criteria
            filter_criteria = {}
            if data_type:
                filter_criteria["data_type"] = data_type
            
            # Add keywords filter if provided
            if keywords:
                # Use regex to search for keywords that contain the provided string
                filter_criteria["keywords"] = {"$regex": keywords, "$options": "i"}
            
            # Add title filter if provided
            if title:
                # Use regex to search for title containing the provided string
                filter_criteria["title"] = {"$regex": title, "$options": "i"}
            
            if not query and (data_type or keywords or title):
                # If only filter criteria are provided (no full-text search)
                return await self.data_ingestion_repository.count_by_criteria(filter_criteria)
            elif not query:
                # If no filters, count all items
                return await self.data_ingestion_repository.count()
            else:
                # For query-based search, we need to get IDs from Pinecone
                search_results = await self.pinecone_repository.search(
                    query=query,
                    limit=1000  # Use a large limit to get most matches for counting
                )
                
                if not data_type and not keywords and not title:
                    return len(search_results)
                
                # Apply filters
                filtered_count = 0
                for result in search_results:
                    mongodb_id = result["id"]
                    data_item = await self.data_ingestion_repository.find_by_id(mongodb_id)
                    
                    if not data_item:
                        continue
                    
                    # Apply data_type filter
                    if data_type and data_item.data_type != data_type:
                        continue
                    
                    # Apply keywords filter
                    if keywords and not any(keywords.lower() in keyword.lower() for keyword in data_item.keywords):
                        continue
                    
                    # Apply title filter
                    if title and title.lower() not in data_item.title.lower():
                        continue
                    
                    filtered_count += 1
                
                return filtered_count
        except Exception as e:
            self.logger.error(f"Error counting data ingestion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error counting data: {str(e)}")
    
    async def delete_data_ingestion(self, data_id: str, user: Optional[User] = None) -> bool:
        """
        Delete data ingestion and associated resources.
        
        Args:
            data_id: Data ingestion ID
            user: User performing the deletion
            
        Returns:
            bool: True if deletion successful
        """
        # Get data ingestion
        data_ingestion = await self.data_ingestion_repository.get_by_id(data_id)
        
        if not data_ingestion:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        # Delete from Pinecone if ID exists
        if data_ingestion.pinecone_id:
            await self.pinecone_repository.delete_vector(data_ingestion.pinecone_id)
        
        # Delete file from S3 if URL exists
        # if data_ingestion.file_url:
        #     await self.s3_repository.delete_file(data_ingestion.file_url)
        
        # Delete from MongoDB
        deleted = await self.data_ingestion_repository.delete(data_id)
        
        return deleted
    
    async def process_list_data_ingestion(
        self,
        page: int = 1,
        page_size: int = 10,
        query: str = "",
        data_type: Optional[str] = None,
        keywords: Optional[str] = None,
        title_like: Optional[str] = None,
        data_type_like: Optional[str] = None,
        keywords_like: Optional[str] = None,
        _page: Optional[int] = None,
        _pageSize: Optional[int] = None,
        _sort: Optional[str] = None,
        _order: Optional[str] = None,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Process list data ingestion request with all parameters and return standardized response.
        
        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 10)
            query: Optional search query to filter results
            data_type: Optional data type filter
            keywords: Optional keywords filter
            title_like: Filter title containing this string
            data_type_like: Filter data_type containing this string
            keywords_like: Filter keywords containing this string
            _page: Alternative page parameter (used by refine)
            _pageSize: Alternative page size parameter (used by refine)
            _sort: Field to sort by (used by refine)
            _order: Sort order (asc or desc, used by refine)
            user: User performing the request
            
        Returns:
            Dict[str, Any]: Standardized response with data, pagination info, and schema
        """
        try:
            # Use refine parameters if provided
            actual_page = _page if _page is not None else page
            actual_page_size = _pageSize if _pageSize is not None else page_size
            
            # Handle filter parameters
            # Priority: *_like parameters > direct parameters
            actual_title = title_like if title_like is not None else None
            actual_data_type = data_type_like if data_type_like is not None else data_type
            actual_keywords = keywords_like if keywords_like is not None else keywords
            
            # Get total count for pagination
            total_count = await self.count_data_ingestion(
                query=query, 
                data_type=actual_data_type, 
                keywords=actual_keywords,
                title=actual_title,
                user=user
            )
            
            # Calculate pagination values
            total_pages = (total_count + actual_page_size - 1) // actual_page_size
            skip = (actual_page - 1) * actual_page_size
            
            # Get search results with pagination and sorting
            result_items = await self.list_data_ingestion(
                query=query,
                data_type=actual_data_type,
                keywords=actual_keywords,
                title=actual_title,
                skip=skip,
                limit=actual_page_size,
                sort_field=_sort,
                sort_order=_order,
                user=user
            )
            
            # Return standardized response format
            return {
                "data": result_items,
                "page": actual_page,
                "page_size": actual_page_size,
                "total_page": total_pages,
                "total_data": total_count
            }
        except Exception as e:
            self.logger.error(f"Error processing list data ingestion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing list data: {str(e)}") 