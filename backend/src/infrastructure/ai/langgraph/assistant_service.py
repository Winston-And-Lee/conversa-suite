"""
Service to manage assistant-ui interactions with LangGraph.
"""
import logging
import uuid
import asyncio
from anyio import get_cancelled_exc_class
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime

from .assistant import create_assistant_ui_agent
from src.infrastructure.database.mongodb import MongoDB
from src.interface.repository.database.db_repository import thread_repository
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from ..model import create_llm

logger = logging.getLogger(__name__)

# Create the assistant graph once
assistant_graph = create_assistant_ui_agent()

# Helper functions
async def process_chat_request(messages: List[Dict[str, Any]], system_message: Optional[str] = None) -> str:
    """
    Process a chat request using the assistant graph.
    
    Args:
        messages: The messages in the conversation
        system_message: Optional system message to guide the assistant
        
    Returns:
        The assistant's response text
    """
    try:
        # Convert messages to LangChain format for the LLM
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        lc_messages = []
        
        # Add system message if provided
        if system_message:
            lc_messages.append(SystemMessage(content=system_message))
        
        # Add conversation messages
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system" and not system_message:
                lc_messages.append(SystemMessage(content=msg["content"]))
        
        # Create the language model
        from ..model import create_llm
        llm = create_llm(
            run_name=f"Chat Processing",
            metadata={"source": "conversa_suite_api"}
        )
        
        # Get response from LLM
        response = llm.invoke(lc_messages)
        return response.content
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return an error message
        return "I apologize, but I'm experiencing technical difficulties. Please try again later."

async def generate_thread_summary(messages: List[Dict[str, Any]]) -> str:
    """
    Generate a summary for a thread based on its messages.
    
    Args:
        messages: The messages in the thread
        
    Returns:
        A summary of the conversation
    """
    # For now, just use the last few messages as a summary
    if not messages:
        return "Empty conversation"
    
    # Get the last user message
    last_user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_message = msg.get("content", "")
            break
    
    # Create a simple summary
    if last_user_message:
        summary = last_user_message[:100]
        if len(last_user_message) > 100:
            summary += "..."
        return summary
    
    return "Conversation in progress"

class AssistantUIService:
    """Service to manage assistant-ui interactions."""
    
    def __init__(self):
        """Initialize the service."""
        # The repository will be lazily loaded when needed
        self._thread_repository = None
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
    
    async def _get_thread_repository(self):
        """Get the thread repository lazily and ensure database connection."""
        if self._thread_repository is None:
            # Ensure MongoDB connection is established
            try:
                await MongoDB.reconnect_if_needed()
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                # Continue anyway, the repository will handle the error
            
            # Use the factory function from db_repository
            self._thread_repository = thread_repository()
        return self._thread_repository
    
    async def send_message(self, thread_id: str, content: str) -> Dict[str, Any]:
        """Send a message to the assistant and get a response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Get current thread from repository
            thread_repo = await self._get_thread_repository()
            thread = await thread_repo.get_thread(thread_id)
            
            # Check if thread exists
            if not thread:
                logger.error(f"Thread {thread_id} not found")
                raise ValueError(f"Thread {thread_id} not found")
            
            # Add user message to the thread messages
            user_message = {
                "role": "user",
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            await thread_repo.add_message_to_thread(thread_id, user_message)
            
            # Get the updated thread to ensure we have the latest messages
            thread = await thread_repo.get_thread(thread_id)
            
            # Get all messages from the thread object
            thread_messages = []
            if hasattr(thread, "messages"):
                thread_messages = thread.messages
            else:
                logger.warning(f"Thread {thread_id} has no messages attribute, using empty list")
            
            # Process the message with the assistant
            try:
                # Get system message if available
                system_message = thread.system_message if hasattr(thread, "system_message") else None
                
                # Run the assistant
                assistant_response = await process_chat_request(thread_messages, system_message)
                
                # Add assistant message to the thread messages
                assistant_message = {
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await thread_repo.add_message_to_thread(thread_id, assistant_message)
                
                # Update the thread summary
                summary = await generate_thread_summary(thread_messages + [assistant_message])
                await thread_repo.update_thread_summary(thread_id, summary)
                
                # Return the response
                return {
                    "thread_id": thread_id,
                    "messages": [
                        {"role": "user", "content": content},
                        {"role": "assistant", "content": assistant_response}
                    ]
                }
            except CancelledExc:
                logger.warning(f"Request for thread {thread_id} was cancelled")
                raise
            except Exception as e:
                logger.error(f"Error processing message for thread {thread_id}: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Error in send_message for thread {thread_id}: {str(e)}")
            raise
    
    async def stream_message(self, thread_id: str, content: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream a message to the assistant and get streaming response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Get current thread from repository
            thread_repo = await self._get_thread_repository()
            thread = await thread_repo.get_thread(thread_id)
            
            # Check if thread exists
            if not thread:
                logger.error(f"Thread {thread_id} not found")
                raise ValueError(f"Thread {thread_id} not found")
            
            # Get all messages from the thread object
            thread_messages = []
            if hasattr(thread, "messages"):
                thread_messages = thread.messages
            else:
                logger.warning(f"Thread {thread_id} has no messages attribute, using empty list")
            
            # Create tracing metadata
            metadata = {
                "thread_id": thread_id,
                "assistant_id": getattr(thread, "assistant_id", "default"),
                "message_count": len(thread_messages),
                "source": "conversa_suite_api"
            }
            
            # Convert messages to LangChain format for the LLM
            lc_messages = []
            
            # Add system message if available
            system_message = thread.system_message if hasattr(thread, "system_message") else None
            if system_message:
                lc_messages.append(SystemMessage(content=system_message))
            
            # Add conversation messages
            for msg in thread_messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system" and not system_message:
                    lc_messages.append(SystemMessage(content=msg["content"]))
            
            # Create the language model
            llm = create_llm(
                run_name=f"Thread {thread_id[:8]} - Streaming",
                metadata=metadata,
                streaming=True
            )
            
            # First, check if the message is about fiction
            is_fiction = False
            fiction_results = []
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
                # Create a placeholder for the assistant's response
                messages_with_response = thread_messages + [{
                    "role": "assistant",
                    "content": ""
                }]
                
                async for chunk in llm.astream(lc_messages):
                    # Append the new content to the assistant's response
                    assistant_response += chunk.content
                    
                    # Update the last message with the accumulated response
                    messages_with_response[-1]["content"] = assistant_response
                    
                    # Prepare response with fiction detection info
                    response = {
                        "thread_id": thread_id,
                        "messages": messages_with_response
                    }
                    
                    # Add fiction detection info if available
                    if is_fiction:
                        response["is_fiction_topic"] = is_fiction
                        
                        # Include pinecone results summary if it's a fiction topic
                        if fiction_results:
                            response["fiction_sources"] = [
                                {
                                    "title": item.get("title", "Untitled"),
                                    "reference": item.get("reference", ""),
                                    "similarity_score": item.get("similarity_score", 0.0)
                                }
                                for item in fiction_results
                            ]
                    
                    # Yield the updated response
                    yield response
                
                # Save the final assistant message to the thread
                if assistant_response:
                    assistant_message = {
                        "role": "assistant",
                        "content": assistant_response,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await thread_repo.add_message_to_thread(thread_id, assistant_message)
                    
                    # Update the thread summary
                    summary = await generate_thread_summary(thread_messages + [assistant_message])
                    await thread_repo.update_thread_summary(thread_id, summary)
                
                logger.info(f"Successfully completed streaming for thread {thread_id}")
                
            except (CancelledExc, asyncio.CancelledError) as e:
                # Client disconnected - still save what we generated so far
                logger.info(f"Streaming cancelled for thread {thread_id}, saving partial response")
                if assistant_response:
                    assistant_message = {
                        "role": "assistant",
                        "content": assistant_response,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await thread_repo.add_message_to_thread(thread_id, assistant_message)
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
        """Get messages for a thread."""
        try:
            # Get thread from repository
            thread_repo = await self._get_thread_repository()
            thread = await thread_repo.get_thread(thread_id)
            
            # Check if thread exists
            if not thread:
                logger.error(f"Thread {thread_id} not found")
                raise ValueError(f"Thread {thread_id} not found")
            
            # Return the messages
            if hasattr(thread, "messages"):
                return thread.messages
            else:
                logger.warning(f"Thread {thread_id} has no messages attribute, returning empty list")
                return []
        except Exception as e:
            logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
            raise
    
    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread."""
        try:
            # Delete thread from repository
            thread_repo = await self._get_thread_repository()
            result = await thread_repo.delete_thread(thread_id)
            
            logger.info(f"Deleted thread {thread_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error deleting thread {thread_id}: {str(e)}")
            raise


# Create singleton instance
assistant_service = AssistantUIService() 