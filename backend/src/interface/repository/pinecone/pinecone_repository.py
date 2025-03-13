import os
import uuid
import logging
import tempfile
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
import requests
import re

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader,
    WebBaseLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config.settings import get_settings


class PineconeRepository:
    """Repository for interacting with Pinecone vector database."""

    def __init__(self):
        """Initialize the Pinecone repository with API key and environment."""
        # Get settings from configuration
        settings = get_settings()
        
        self.api_key = settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENVIRONMENT  # Now used as region
        self.cloud = settings.PINECONE_CLOUD
        self.index_name = settings.PINECONE_INDEX_NAME
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        
        self.logger = logging.getLogger(__name__)
        
        # Log configuration (masked for security)
        self.logger.info(f"Initializing Pinecone with index: {self.index_name}")
        self.logger.debug(f"Pinecone cloud: {self.cloud}, region: {self.environment}")
        
        if not all([self.api_key, self.environment, self.index_name, self.openai_api_key]):
            self.logger.error("Missing Pinecone or OpenAI configuration")
            raise ValueError("Missing Pinecone or OpenAI configuration")
        
        # Initialize Pinecone with new method
        try:
            # Create Pinecone client
            self.pc = Pinecone(api_key=self.api_key)
            self.logger.info("Pinecone client initialized successfully")
            
            # Get the index or create if it doesn't exist
            if self.index_name not in self.pc.list_indexes().names():
                self.logger.info(f"Creating new Pinecone index: {self.index_name}")
                # Create a new index with a dimension of 1536 for OpenAI embeddings
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI's text-embedding-3 model uses 1536 dimensions
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.environment
                    )
                )
                self.logger.info(f"Created new Pinecone index: {self.index_name}")
            else:
                self.logger.info(f"Using existing Pinecone index: {self.index_name}")
                
            # Get the index
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            self.logger.error(f"Pinecone initialization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Pinecone initialization error: {str(e)}")
        
        # Initialize OpenAI client
        try:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"OpenAI client initialization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI client initialization error: {str(e)}")
    
    async def load_webpage(self, webpage_url: str, metadata: dict) -> List[str]:
        """
        Load content from a webpage URL, extract text, and store in Pinecone.
        
        Args:
            webpage_url: URL of the webpage to load
            metadata: Metadata to store with the vectors
            
        Returns:
            List[str]: List of vector IDs created in Pinecone
        """
        try:
            self.logger.info(f"Loading webpage from URL: {webpage_url}")
            
            # Validate URL format
            if not re.match(r'^https?://', webpage_url):
                self.logger.error(f"Invalid URL format: {webpage_url}")
                raise ValueError(f"Invalid URL format: {webpage_url}. URL must start with http:// or https://")
            
            # Use WebBaseLoader to load the webpage
            try:
                loader = WebBaseLoader(webpage_url)
                documents = loader.load()
                self.logger.info(f"Loaded {len(documents)} document(s) from webpage")
                
                # Extract webpage title if available
                webpage_title = ""
                if documents and hasattr(documents[0], "metadata") and "title" in documents[0].metadata:
                    webpage_title = documents[0].metadata["title"]
                    self.logger.info(f"Extracted webpage title: {webpage_title}")
                
                # Split the documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=10000,
                    chunk_overlap=100
                )
                chunks = text_splitter.split_documents(documents)
                self.logger.info(f"Split webpage into {len(chunks)} chunks")
                
                # Store each chunk in Pinecone
                vector_ids = []
                for i, chunk in enumerate(chunks):
                    try:
                        print(f"[PINECONE] Processing chunk {i+1}/{len(chunks)}...")
                        # Create a unique ID for each chunk
                        chunk_id = f"{metadata.get('mongodb_id', str(uuid.uuid4()))}_chunk_{i}"
                        
                        # Create text data for embedding
                        text_data = {
                            "title": metadata.get("title", webpage_title),
                            "specified_text": metadata.get("specified_text", ""),
                            "content": metadata.get("content", ""),
                            "file_text": chunk.page_content,
                            "keywords": []
                        }
                        
                        # Add chunk-specific metadata
                        chunk_metadata = metadata.copy()
                        chunk_metadata["chunk_id"] = chunk_id
                        chunk_metadata["chunk_index"] = i
                        chunk_metadata["total_chunks"] = len(chunks)
                        chunk_metadata["source_type"] = "webpage"
                        chunk_metadata["webpage_url"] = webpage_url
                        
                        # Handle document metadata safely
                        if hasattr(chunk, "metadata"):
                            # Extract only simple values from metadata
                            safe_metadata = {}
                            for key, value in chunk.metadata.items():
                                # Only include simple types that Pinecone accepts
                                if isinstance(value, (str, int, float, bool)) or (
                                    isinstance(value, list) and all(isinstance(item, str) for item in value)
                                ):
                                    safe_metadata[f"doc_{key}"] = value
                            
                            # Add safe metadata to chunk metadata
                            chunk_metadata.update(safe_metadata)
                        
                        # Filter out None values from metadata
                        chunk_metadata = self._filter_none_values(chunk_metadata)
                        
                        # Store in Pinecone
                        vector_id = await self.upsert_vector(text_data, chunk_metadata)
                        vector_ids.append(vector_id)
                    except Exception as chunk_error:
                        self.logger.error(f"Error processing chunk {i}: {str(chunk_error)}")
                        # Continue with next chunk
                        continue
                
                if vector_ids:
                    self.logger.info(f"Successfully stored {len(vector_ids)} vectors in Pinecone")
                    return vector_ids
                else:
                    raise ValueError("Failed to store any chunks in Pinecone")
                
            except Exception as e:
                self.logger.error(f"Error processing webpage: {str(e)}")
                raise
                
        except Exception as e:
            self.logger.error(f"Error loading webpage from URL: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading webpage from URL: {str(e)}")
    
    async def load_file_from_url(self, file_url: str, metadata: dict) -> List[str]:
        """
        Load a file from a URL, extract text, and store in Pinecone.
        
        Args:
            file_url: URL of the file to load
            metadata: Metadata to store with the vectors
            
        Returns:
            List[str]: List of vector IDs created in Pinecone
        """
        try:
            self.logger.info(f"Loading file from URL: {file_url}")
            
            # Determine file type from URL
            file_extension = file_url.split(".")[-1].lower()
            
            if file_extension not in ["pdf", "docx", "doc", "txt"]:
                self.logger.error(f"Unsupported file type: {file_extension}")
                raise ValueError(f"Unsupported file type: {file_extension}. Supported types are: pdf, docx, doc, txt")
            
            # Download the file to a temporary location
            with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
                response = requests.get(file_url, stream=True)
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                
                temp_file_path = temp_file.name
            
            self.logger.info(f"File downloaded to temporary location: {temp_file_path}")
            
            # Load the document based on file type
            try:
                if file_extension == "pdf":
                    loader = PyPDFLoader(temp_file_path)
                elif file_extension in ["docx", "doc"]:
                    loader = Docx2txtLoader(temp_file_path)
                elif file_extension == "txt":
                    loader = TextLoader(temp_file_path)
                else:
                    # Fallback to unstructured loader
                    loader = UnstructuredFileLoader(temp_file_path)
                
                documents = loader.load()
                self.logger.info(f"Loaded {len(documents)} document(s) from file")
                
                # Split the documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100
                )
                chunks = text_splitter.split_documents(documents)
                self.logger.info(f"Split documents into {len(chunks)} chunks")
                
                # Store each chunk in Pinecone
                vector_ids = []
                for i, chunk in enumerate(chunks):
                    try:
                        # Create a unique ID for each chunk
                        chunk_id = f"{metadata.get('mongodb_id', str(uuid.uuid4()))}_chunk_{i}"
                        
                        # Create text data for embedding
                        text_data = {
                            "title": metadata.get("title", ""),
                            "specified_text": metadata.get("specified_text", ""),
                            "content": metadata.get("content", ""),
                            "file_text": chunk.page_content,
                            "keywords": []
                        }
                        
                        # Add chunk-specific metadata
                        chunk_metadata = metadata.copy()
                        chunk_metadata["chunk_id"] = chunk_id
                        chunk_metadata["chunk_index"] = i
                        chunk_metadata["total_chunks"] = len(chunks)
                        chunk_metadata["source_type"] = "file"
                        
                        # Handle document metadata safely
                        if hasattr(chunk, "metadata"):
                            # Extract only simple values from metadata
                            safe_metadata = {}
                            for key, value in chunk.metadata.items():
                                # Only include simple types that Pinecone accepts
                                if isinstance(value, (str, int, float, bool)) or (
                                    isinstance(value, list) and all(isinstance(item, str) for item in value)
                                ):
                                    safe_metadata[f"doc_{key}"] = value
                            
                            # Add safe metadata to chunk metadata
                            chunk_metadata.update(safe_metadata)
                        
                        # Filter out None values from metadata
                        chunk_metadata = self._filter_none_values(chunk_metadata)
                        
                        # Store in Pinecone
                        vector_id = await self.upsert_vector(text_data, chunk_metadata)
                        vector_ids.append(vector_id)
                    except Exception as chunk_error:
                        self.logger.error(f"Error processing chunk {i}: {str(chunk_error)}")
                        # Continue with next chunk
                        continue
                
                if vector_ids:
                    self.logger.info(f"Successfully stored {len(vector_ids)} vectors in Pinecone")
                    
                    # Clean up the temporary file
                    os.unlink(temp_file_path)
                    
                    return vector_ids
                else:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)
                    raise ValueError("Failed to store any chunks in Pinecone")
                
            except Exception as e:
                self.logger.error(f"Error processing file: {str(e)}")
                # Clean up the temporary file in case of error
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise
                
        except Exception as e:
            self.logger.error(f"Error loading file from URL: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error loading file from URL: {str(e)}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            self.logger.debug(f"Generating embeddings for text (length: {len(text)})")
            # Generate embedding using OpenAI's text-embedding-3 model
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            # Extract embeddings from response
            embedding = response.data[0].embedding
            self.logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"OpenAI embedding generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Embedding generation error: {str(e)}")
    
    def _filter_none_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out None values from a dictionary.
        
        Args:
            data: Dictionary that may contain None values
            
        Returns:
            Dict[str, Any]: Dictionary with None values removed
        """
        if not data:
            return {}
            
        filtered_data = {}
        for key, value in data.items():
            if value is not None:
                if isinstance(value, dict):
                    filtered_data[key] = self._filter_none_values(value)
                elif isinstance(value, list):
                    if all(not isinstance(item, dict) for item in value):
                        filtered_data[key] = value
                    else:
                        filtered_data[key] = [
                            self._filter_none_values(item) if isinstance(item, dict) else item
                            for item in value
                        ]
                else:
                    filtered_data[key] = value
        return filtered_data
    
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
                text_data.get("content", ""),
                text_data.get("file_text", ""),
                " ".join(text_data.get("keywords", []))
            ])
            
            self.logger.debug(f"Upserting vector with metadata: {metadata.get('mongodb_id', 'unknown')}")
            
            # Generate embedding
            embedding = await self.generate_embeddings(combined_text)
            
            # Generate a unique ID if not provided
            vector_id = metadata.get("id") or str(uuid.uuid4())
            
            # Filter out None values from metadata
            filtered_metadata = self._filter_none_values(metadata)
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": filtered_metadata
                    }
                ]
            )
            
            self.logger.info(f"Successfully upserted vector with ID: {vector_id}")
            return vector_id
            
        except Exception as e:
            self.logger.error(f"Pinecone upsert error: {str(e)}")
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
            self.logger.info(f"Deleting vector with ID: {vector_id}")
            self.index.delete(ids=[vector_id])
            self.logger.info(f"Successfully deleted vector with ID: {vector_id}")
            return True
        except Exception as e:
            self.logger.error(f"Pinecone delete error: {str(e)}")
            return False
    
    async def search(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Perform semantic search using query text.
        
        Args:
            query: Query text
            limit: Maximum number of results
            offset: Number of results to skip (for pagination)
            
        Returns:
            List[Dict[str, Any]]: List of search results with metadata and scores
        """
        try:
            self.logger.info(f"Performing semantic search with query: '{query}' (limit: {limit}, offset: {offset})")
            
            # Generate embedding for query
            query_embedding = await self.generate_embeddings(query)
            
            # Query Pinecone with a higher limit to account for chunked documents
            # We'll need to group by mongodb_id later
            raw_limit = (limit + offset) * 3  # Get more results to account for chunking
            results = self.index.query(
                vector=query_embedding,
                top_k=raw_limit,  # Get extra results
                include_metadata=True
            )
            
            # Group results by mongodb_id and take the highest scoring match
            grouped_results = {}
            for match in results.matches:
                mongodb_id = match.metadata.get("mongodb_id")
                if not mongodb_id:
                    continue
                
                # If we haven't seen this ID yet, or if this match has a higher score
                if mongodb_id not in grouped_results or match.score > grouped_results[mongodb_id]["score"]:
                    # Store the match with its score
                    grouped_results[mongodb_id] = {
                        "id": mongodb_id,
                        "title": match.metadata.get("title"),
                        "specified_text": match.metadata.get("specified_text"),
                        "data_type": match.metadata.get("data_type"),
                        "content": match.metadata.get("content"),
                        "reference": match.metadata.get("reference"),
                        "file_url": match.metadata.get("file_url"),
                        "webpage_url": match.metadata.get("webpage_url"),
                        "source_type": match.metadata.get("source_type", "text"),
                        "user_id": match.metadata.get("user_id"),
                        "similarity_score": match.score,
                        # Include chunk information if available
                        "chunk_id": match.metadata.get("chunk_id"),
                        "chunk_index": match.metadata.get("chunk_index"),
                        "total_chunks": match.metadata.get("total_chunks"),
                        # Include source metadata string if available
                        "source_metadata_str": match.metadata.get("source_metadata_str")
                    }
            
            # Convert to list and sort by score
            formatted_results = list(grouped_results.values())
            formatted_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Apply pagination
            paginated_results = formatted_results[offset:offset + limit] if offset > 0 else formatted_results[:limit]
            
            self.logger.info(f"Search returned {len(paginated_results)} results after grouping")
            return paginated_results
            
        except Exception as e:
            self.logger.error(f"Pinecone search error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")
    
    # For backward compatibility
    async def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Legacy method for semantic search (for backward compatibility).
        
        Args:
            query: Query text
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of search results with metadata and scores
        """
        self.logger.debug(f"Using legacy semantic_search method, redirecting to search")
        return await self.search(query=query, limit=limit)
            
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
            self.logger.debug(f"Generating keywords from text (length: {len(text)})")
            
            # Use OpenAI to generate keywords
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
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
            
            self.logger.info(f"Generated {len(keywords)} keywords: {', '.join(keywords)}")
            return keywords
            
        except Exception as e:
            self.logger.error(f"Keyword generation error: {str(e)}")
            return [] 