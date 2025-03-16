"""
Service to manage assistant-ui interactions with LangGraph.
"""
import logging
import uuid
import asyncio
import anyio
from anyio import get_cancelled_exc_class
from typing import Dict, List, Optional, Any, AsyncIterator
import json

from .assistant import create_assistant_ui_agent, create_initial_state, AssistantUIState
from src.infrastructure.database.mongodb import MongoDB

logger = logging.getLogger(__name__)

# Create the assistant graph once
assistant_graph = create_assistant_ui_agent()

class AssistantUIService:
    """Service to manage assistant-ui interactions."""
    
    def __init__(self):
        """Initialize the service."""
        # The repository will be lazily loaded when needed
        self._session_repository = None
        # Initialize MongoDB connection in the background
        asyncio.create_task(self._init_mongodb())
    
    async def _init_mongodb(self):
        """Initialize MongoDB connection in the background."""
        try:
            logger.info("Initializing MongoDB connection for AssistantUIService")
            await MongoDB.connect_to_database()
            logger.info("MongoDB connection initialized for AssistantUIService")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
    
    async def _get_session_repository(self):
        """Get the session repository lazily and ensure database connection."""
        if self._session_repository is None:
            # Import here to avoid circular imports
            from src.interface.repository.mongodb.session_repository import MongoDBSessionRepository
            
            # Ensure MongoDB connection is established
            try:
                await MongoDB.reconnect_if_needed()
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                # Continue anyway, the repository will handle the error
            
            self._session_repository = MongoDBSessionRepository()
        return self._session_repository
    
    async def create_thread(self, system_message: Optional[str] = None, assistant_id: Optional[str] = None) -> str:
        """Create a new assistant thread."""
        thread_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state = create_initial_state(assistant_id, system_message)
        
        # Store the state in the repository
        session_repo = await self._get_session_repository()
        await session_repo.save_session(thread_id, initial_state)
        
        logger.info(f"Created new assistant thread: {thread_id}")
        return thread_id
    
    async def send_message(self, thread_id: str, content: str) -> Dict[str, Any]:
        """Send a message to the assistant and get a response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Get current state from repository
            session_repo = await self._get_session_repository()
            current_state = await session_repo.get_session(thread_id)
            
            # Check if thread exists
            if not current_state:
                logger.warning(f"Thread not found: {thread_id}")
                return {"error": "Thread not found"}
            
            # Add user message to the messages
            current_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Create tracing metadata
            metadata = {
                "thread_id": thread_id,
                "assistant_id": current_state.get("metadata", {}).get("assistant_id", "default"),
                "message_count": len(current_state.get("messages", [])),
                "source": "conversa_suite_api"
            }
            
            # Update metadata in state
            if "metadata" not in current_state:
                current_state["metadata"] = {}
            current_state["metadata"].update(metadata)
            
            # Run the agent graph
            result = await assistant_graph.ainvoke(current_state)
            
            # Update session state in repository
            await session_repo.save_session(thread_id, result)
            
            # Return formatted response with fiction detection info
            response = {
                "thread_id": thread_id,
                "messages": result["messages"]
            }
            
            # Add fiction detection info if available
            if "is_fiction_topic" in result:
                response["is_fiction_topic"] = result["is_fiction_topic"]
                
                # Include pinecone results summary if it's a fiction topic
                if result["is_fiction_topic"] and result.get("pinecone_results"):
                    response["fiction_sources"] = [
                        {
                            "title": item.get("title", "Untitled"),
                            "reference": item.get("reference", ""),
                            "similarity_score": item.get("similarity_score", 0.0)
                        }
                        for item in result.get("pinecone_results", [])
                    ]
            
            return response
            
        except (CancelledExc, asyncio.CancelledError) as e:
            logger.info(f"Operation cancelled for thread {thread_id}: {str(e)}")
            # Return a partial result if possible
            return {
                "thread_id": thread_id,
                "messages": current_state.get("messages", [])
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    async def stream_message(self, thread_id: str, content: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream a message to the assistant and get streaming response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Get current state from repository
            session_repo = await self._get_session_repository()
            current_state = await session_repo.get_session(thread_id)
            
            # Check if thread exists
            if not current_state:
                logger.warning(f"Thread not found: {thread_id}")
                yield {"error": "Thread not found"}
                return
            
            # Add user message to the messages
            current_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Create a placeholder for the assistant's response
            current_state["messages"].append({
                "role": "assistant",
                "content": ""
            })
            
            # Create tracing metadata
            metadata = {
                "thread_id": thread_id,
                "assistant_id": current_state.get("metadata", {}).get("assistant_id", "default"),
                "message_count": len(current_state.get("messages", [])),
                "source": "conversa_suite_api"
            }
            
            # Update metadata in state
            if "metadata" not in current_state:
                current_state["metadata"] = {}
            current_state["metadata"].update(metadata)
            
            # Initialize fiction detection fields
            current_state["is_fiction_topic"] = False
            current_state["pinecone_results"] = []
            
            # Convert messages to LangChain format for the LLM
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            lc_messages = []
            for msg in current_state["messages"][:-1]:  # Exclude the empty assistant message
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
            
            # Create the language model
            from ..model import create_llm
            llm = create_llm(
                run_name=f"Thread {thread_id[:8]} - Streaming",
                metadata=metadata,
                streaming=True
            )
            
            # First, check if the message is about fiction
            try:
                # Use a separate LLM call to classify the topic
                classification_prompt = [
                    SystemMessage(content="You are a topic classifier. Determine if the user's message is about fiction (novels, stories, fairy tales, etc.). Respond with only 'YES' if it's about fiction or 'NO' if it's not."),
                    HumanMessage(content=content)
                ]
                
                classification_llm = create_llm(
                    run_name="Fiction Topic Classification - Streaming",
                    metadata={"task": "fiction_classification"}
                )
                
                classification_result = classification_llm.invoke(classification_prompt)
                is_fiction = "YES" in classification_result.content.upper()
                
                # Update state with classification result
                current_state["is_fiction_topic"] = is_fiction
                
                # If it's about fiction, query Pinecone
                if is_fiction:
                    logger.info(f"Detected fiction topic in streaming message: {content[:50]}...")
                    
                    # Import and initialize Pinecone repository
                    from src.interface.repository.database.db_repository import pinecone_repository
                    pinecone_repo = pinecone_repository()
                    
                    # Query Pinecone
                    search_results = await pinecone_repo.search(content, limit=5)
                    
                    # Filter results to only include fiction
                    fiction_results = [
                        result for result in search_results 
                        if result.get("data_type") == "FICTION" or 
                           result.get("source_type") == "fiction"
                    ]
                    
                    # Ensure each result has a similarity_score field
                    for result in fiction_results:
                        if "similarity_score" not in result:
                            # Use a default score if missing
                            result["similarity_score"] = 0.0
                    
                    # Update state with Pinecone results
                    current_state["pinecone_results"] = fiction_results
                    logger.info(f"Found {len(fiction_results)} fiction results in Pinecone for streaming")
                    
                    # Add context from Pinecone results
                    if fiction_results:
                        context = "I found the following fiction-related information that might be helpful:\n\n"
                        for i, result in enumerate(fiction_results, 1):
                            title = result.get("title", "Untitled")
                            content_text = result.get("content", "")
                            specified_text = result.get("specified_text", "")
                            reference = result.get("reference", "")
                            
                            context += f"{i}. {title}\n"
                            if specified_text:
                                context += f"   Quote: \"{specified_text}\"\n"
                            if content_text:
                                context += f"   Summary: {content_text}\n"
                            if reference:
                                context += f"   Reference: {reference}\n"
                            context += "\n"
                        
                        # Add context as a system message
                        lc_messages.insert(0, SystemMessage(content=context))
            except Exception as e:
                logger.error(f"Error in fiction detection during streaming: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue without fiction detection
            
            # Stream the response
            assistant_response = ""
            try:
                async for chunk in llm.astream(lc_messages):
                    # Append the new content to the assistant's response
                    assistant_response += chunk.content
                    
                    # Update the last message with the accumulated response
                    current_state["messages"][-1]["content"] = assistant_response
                    
                    # Periodically save the state to the repository
                    if len(assistant_response) % 100 == 0:  # Save every ~100 characters
                        await session_repo.save_session(thread_id, current_state)
                    
                    # Prepare response with fiction detection info
                    response = {
                        "thread_id": thread_id,
                        "messages": current_state["messages"]
                    }
                    
                    # Add fiction detection info if available
                    if current_state.get("is_fiction_topic"):
                        response["is_fiction_topic"] = current_state["is_fiction_topic"]
                        
                        # Include pinecone results summary if it's a fiction topic
                        if current_state["is_fiction_topic"] and current_state.get("pinecone_results"):
                            response["fiction_sources"] = [
                                {
                                    "title": item.get("title", "Untitled"),
                                    "reference": item.get("reference", ""),
                                    "similarity_score": item.get("similarity_score", 0.0)
                                }
                                for item in current_state.get("pinecone_results", [])
                            ]
                    
                    # Yield the updated response
                    yield response
                
                # Save the final state to the repository
                await session_repo.save_session(thread_id, current_state)
                logger.info(f"Successfully completed streaming for thread {thread_id}")
                
            except (CancelledExc, asyncio.CancelledError) as e:
                # Client disconnected - still save what we generated so far
                logger.info(f"Streaming cancelled for thread {thread_id}, saving partial response")
                if assistant_response:
                    current_state["messages"][-1]["content"] = assistant_response
                    await session_repo.save_session(thread_id, current_state)
                raise  # Re-raise to be caught by the outer handler
            
        except (CancelledExc, asyncio.CancelledError) as e:
            # This will be caught by the routes and handled there
            logger.info(f"Stream cancelled for thread {thread_id}")
            raise
        except Exception as e:
            logger.error(f"Error processing streaming message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            yield {"error": str(e)}
    
    async def get_thread_messages(self, thread_id: str) -> List[Dict[str, str]]:
        """Get the message history for a thread."""
        # Get state from repository
        session_repo = await self._get_session_repository()
        state = await session_repo.get_session(thread_id)
        
        if not state:
            logger.warning(f"Thread not found: {thread_id}")
            return []
        
        # Get messages from the state
        return state["messages"]
    
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete an assistant thread."""
        # Delete from repository
        session_repo = await self._get_session_repository()
        result = await session_repo.delete_session(thread_id)
        
        if result:
            logger.info(f"Deleted assistant thread: {thread_id}")
            return True
        
        logger.warning(f"Thread not found for deletion: {thread_id}")
        return False


# Create singleton instance
assistant_service = AssistantUIService() 