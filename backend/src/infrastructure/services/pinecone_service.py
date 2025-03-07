from src.interface.repository.database.db_repository import pinecone_repository
from typing import List, Dict, Any

class PineconeService:
    """Service for interacting with Pinecone vector database."""

    def __init__(self):
        """Initialize the Pinecone service with the Pinecone repository."""
        self.pinecone_repository = pinecone_repository()
    
    async def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """
        Insert or update vectors in Pinecone.
        
        Args:
            vectors: List of vector dictionaries with 'id', 'values', and 'metadata'
            
        Returns:
            bool: True if operation successful
        """
        return await self.pinecone_repository.upsert_vectors(vectors)
    
    async def query_vectors(self, query_vector: List[float], top_k: int = 5, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone.
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List[Dict]: List of matching vectors with scores and metadata
        """
        return await self.pinecone_repository.query_vectors(query_vector, top_k, filter)
    
    async def delete_vectors(self, ids: List[str]) -> bool:
        """
        Delete vectors from Pinecone.
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            bool: True if operation successful
        """
        return await self.pinecone_repository.delete_vectors(ids) 