import os
import uuid
import logging
from typing import List, Dict, Any
from fastapi import HTTPException

import pinecone
from openai import OpenAI


class PineconeRepository:
    """Repository for interacting with Pinecone vector database."""

    def __init__(self):
        """Initialize the Pinecone repository with API key and environment."""
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not all([self.api_key, self.environment, self.index_name, self.openai_api_key]):
            raise ValueError("Missing Pinecone or OpenAI configuration")
        
        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
        # Get the index or create if it doesn't exist
        try:
            if self.index_name not in pinecone.list_indexes():
                # Create a new index with a dimension of 1536 for OpenAI embeddings
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI's text-embedding-3 model uses 1536 dimensions
                    metric="cosine"
                )
            self.index = pinecone.Index(self.index_name)
        except Exception as e:
            logging.error(f"Pinecone initialization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Pinecone initialization error: {str(e)}")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            # Generate embedding using OpenAI's text-embedding-3 model
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            # Extract embeddings from response
            embedding = response.data[0].embedding
            
            return embedding
            
        except Exception as e:
            logging.error(f"OpenAI embedding generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Embedding generation error: {str(e)}")
    
    async def upsert_vector(self, text_data: dict, metadata: dict) -> str:
        """
        Create or update vector in Pinecone.
        
        Args:
            text_data: Dictionary with text fields to embed
            metadata: Metadata to store with the vector
            
        Returns:
            str: Vector ID
        """
        try:
            # Combine all text fields into a single string
            combined_text = " ".join([
                text_data.get("title", ""),
                text_data.get("specified_text", ""),
                text_data.get("file_text", ""),
                " ".join(text_data.get("keywords", []))
            ])
            
            # Generate embedding
            embedding = await self.generate_embeddings(combined_text)
            
            # Generate a unique ID if not provided
            vector_id = metadata.get("id") or str(uuid.uuid4())
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                ]
            )
            
            return vector_id
            
        except Exception as e:
            logging.error(f"Pinecone upsert error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Pinecone upsert error: {str(e)}")
    
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete vector from Pinecone.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            self.index.delete(ids=[vector_id])
            return True
        except Exception as e:
            logging.error(f"Pinecone delete error: {str(e)}")
            return False
    
    async def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search using query text.
        
        Args:
            query: Query text
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of search results with metadata and scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embeddings(query)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    "id": match.metadata.get("mongodb_id"),
                    "title": match.metadata.get("title"),
                    "specified_text": match.metadata.get("specified_text"),
                    "data_type": match.metadata.get("data_type"),
                    "similarity_score": match.score
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Pinecone search error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")
            
    async def generate_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Generate keywords from text using OpenAI.
        
        Args:
            text: Text to generate keywords from
            max_keywords: Maximum number of keywords to generate
            
        Returns:
            List[str]: List of keywords
        """
        try:
            # Use OpenAI to generate keywords
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Generate exactly {max_keywords} relevant keywords in Thai language from the following text. Return only the keywords separated by commas, no explanations:"},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # Extract keywords from response
            keywords_text = response.choices[0].message.content
            
            # Split by comma and clean up
            keywords = [keyword.strip() for keyword in keywords_text.split(",")]
            
            return keywords
            
        except Exception as e:
            logging.error(f"Keyword generation error: {str(e)}")
            return [] 