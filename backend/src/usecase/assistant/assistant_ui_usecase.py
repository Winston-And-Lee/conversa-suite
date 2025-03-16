"""
Assistant UI usecase for handling assistant-ui related business logic.
"""
import logging
import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, AsyncIterator
from anyio import get_cancelled_exc_class

from assistant_stream.assistant_stream_chunk import (
    TextDeltaChunk,
    DataChunk,
    ErrorChunk
)
from assistant_stream.serialization.data_stream import DataStreamResponse

from src.domain.entity.assistant import (
    ChatRequest,
    ChatMessage,
    ThreadModel,
    ThreadListResponse
)
from src.infrastructure.ai.langgraph.assistant_service import assistant_service
from src.interface.repository.mongodb.thread_repository import MongoDBThreadRepository
from src.infrastructure.ai.langgraph.assistant import create_initial_state

logger = logging.getLogger(__name__)

# Default system message for new threads
DEFAULT_SYSTEM_MESSAGE = "You are a helpful AI assistant. Answer the user's questions concisely and accurately."

class AssistantUIUsecase:
    """Usecase class for assistant-ui related operations."""
    
    @staticmethod
    def _get_thread_repository():
        """Get the thread repository."""
        return MongoDBThreadRepository()
    
    @staticmethod
    async def create_thread_and_stream_response(content: str, user_id: str):
        """
        Create a new thread with an initial message and stream the response.
        
        Args:
            content: The initial message content
            user_id: The ID of the user creating the thread
            
        Returns:
            A streaming response with the AI's reply
        """
        thread_id = str(uuid.uuid4())  # Generate thread_id early for error handling
        
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Create the thread data
            thread_data = {
                "thread_id": thread_id,
                "user_id": user_id,
                "title": f"Chat {int(time.time())}",  # Default title
                "summary": content[:100] + "..." if len(content) > 100 else content,
                "messages": [{
                    "role": "user",
                    "content": content,
                    "timestamp": int(time.time() * 1000)
                }],
                "system_message": None,
                "is_archived": False
            }
            
            # Create the thread in MongoDB
            try:
                await thread_repository.create_thread(thread_data)
            except Exception as db_error:
                logger.error(f"Database error when creating thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to create thread: {str(db_error)}")
            
            # Initialize state in assistant_service
            # Create initial state with the same data
            initial_state = create_initial_state("default", thread_data.get("system_message"))
            
            # Add the user message to the initial state
            initial_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Save the state to the assistant service repository
            try:
                session_repo = await assistant_service._get_session_repository()
                await session_repo.save_session(thread_id, initial_state)
            except Exception as db_error:
                logger.error(f"Database error when saving session for thread {thread_id}: {str(db_error)}")
                # Continue anyway since the thread was created, but log the error
                logger.warning(f"Continuing with thread {thread_id} despite session save failure")
            
            logger.info(f"Created new thread {thread_id} for user {user_id}")
            
            # Stream the response directly
            return AssistantUIUsecase._stream_message_generator(
                thread_data=thread_data,
                content=content,
                include_thread_id=True
            )
            
        except ValueError as ve:
            # Create a generator that yields a specific error for ValueError
            async def value_error_generator():
                yield ErrorChunk(error=str(ve))
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(value_error_generator())
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Create a generator that yields an error
            async def error_generator():
                yield ErrorChunk(error=f"Error creating thread: {str(e)}")
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(error_generator())
    
    @staticmethod
    async def add_message_and_stream_response(thread_id: str, content: str, user_id: str):
        """
        Add a message to an existing thread and stream the response.
        
        Args:
            thread_id: The ID of the thread
            content: The message content
            user_id: The ID of the user adding the message
            
        Returns:
            A streaming response with the AI's reply
            
        Raises:
            ValueError: If the thread is not found or the user doesn't have permission
        """
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Get the thread
            try:
                thread = await thread_repository.get_thread(thread_id)
            except Exception as db_error:
                logger.error(f"Database error when getting thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to retrieve thread: {str(db_error)}")
            
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Check if the thread belongs to the current user
            if thread.user_id != user_id:
                raise ValueError("You don't have permission to access this thread")
            
            # Add the message to the thread
            message_data = {
                "role": "user",
                "content": content,
                "timestamp": int(time.time() * 1000)
            }
            
            # Add the message to the thread in MongoDB
            try:
                await thread_repository.add_message_to_thread(thread_id, message_data)
            except Exception as db_error:
                logger.error(f"Database error when adding message to thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to add message to thread: {str(db_error)}")
            
            # Update the summary
            try:
                await thread_repository.update_thread_summary(thread_id, content[:100] + "..." if len(content) > 100 else content)
            except Exception as db_error:
                logger.error(f"Database error when updating thread summary for {thread_id}: {str(db_error)}")
                # Continue despite summary update failure
                logger.warning(f"Continuing with thread {thread_id} despite summary update failure")
            
            # Get the updated thread data
            try:
                updated_thread = await thread_repository.get_thread(thread_id)
                if not updated_thread:
                    logger.error(f"Thread {thread_id} not found after adding message")
                    raise ValueError(f"Thread {thread_id} not found after adding message")
            except Exception as db_error:
                logger.error(f"Database error when getting updated thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to retrieve updated thread: {str(db_error)}")
            
            # Ensure the assistant service has the latest state
            try:
                # First, check if the session exists in the assistant service
                session_repo = await assistant_service._get_session_repository()
                session_state = await session_repo.get_session(thread_id)
                
                if not session_state:
                    # Session doesn't exist in the assistant service, create it
                    logger.info(f"Initializing assistant service state for thread {thread_id}")
                    
                    # Create initial state
                    initial_state = create_initial_state("default", updated_thread.system_message)
                    
                    # Add all messages from the thread data
                    for msg in updated_thread.messages:
                        # Handle both dict and object messages
                        if isinstance(msg, dict):
                            role = msg.get("role")
                            msg_content = msg.get("content")
                        else:
                            role = getattr(msg, "role", None)
                            msg_content = getattr(msg, "content", None)
                            
                        if role and msg_content:
                            initial_state["messages"].append({
                                "role": role,
                                "content": msg_content
                            })
                    
                    # Save the state to the repository
                    await session_repo.save_session(thread_id, initial_state)
                else:
                    # Session exists, add the new message
                    session_state["messages"].append({
                        "role": "user",
                        "content": content
                    })
                    
                    # Save the updated state
                    await session_repo.save_session(thread_id, session_state)
            except Exception as db_error:
                logger.error(f"Database error when managing session state for thread {thread_id}: {str(db_error)}")
                # Continue despite session state issues
                logger.warning(f"Continuing with thread {thread_id} despite session state issues")
            
            logger.info(f"Added message to thread {thread_id} for user {user_id}")
            
            # Stream the response directly
            # The _stream_message_generator will handle the conversion from ThreadModel to dict
            return AssistantUIUsecase._stream_message_generator(
                thread_data=updated_thread,
                content=content,
                include_thread_id=True
            )
            
        except ValueError as ve:
            # Create a generator that yields a specific error for ValueError
            async def value_error_generator():
                yield ErrorChunk(error=str(ve))
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(value_error_generator())
        except Exception as e:
            logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Create a generator that yields an error
            async def error_generator():
                yield ErrorChunk(error=f"Error adding message to thread: {str(e)}")
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(error_generator())
    
    @staticmethod
    async def get_thread(thread_id: str, user_id: str) -> ThreadModel:
        """
        Get a specific thread with its messages.
        
        Args:
            thread_id: The ID of the thread to get
            user_id: The ID of the user requesting the thread
            
        Returns:
            The thread with its messages
            
        Raises:
            ValueError: If the thread is not found or the user doesn't have permission
        """
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Get the thread
            try:
                thread = await thread_repository.get_thread(thread_id)
            except Exception as db_error:
                logger.error(f"Database error when getting thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to retrieve thread: {str(db_error)}")
            
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Check if the thread belongs to the current user
            if not hasattr(thread, "user_id"):
                logger.error(f"Thread {thread_id} has no user_id attribute")
                raise ValueError(f"Invalid thread data: missing user_id")
                
            if thread.user_id != user_id:
                raise ValueError("You don't have permission to access this thread")
            
            return thread
        except ValueError as e:
            # Re-raise ValueError for HTTP-specific handling in the route
            raise e
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Error retrieving thread: {str(e)}")
    
    @staticmethod
    async def get_thread_messages(thread_id: str, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get messages for a specific thread.
        
        Args:
            thread_id: The ID of the thread to get messages for
            user_id: The ID of the user requesting the messages
            
        Returns:
            The messages for the thread
            
        Raises:
            ValueError: If the thread is not found or the user doesn't have permission
        """
        try:
            # Get the thread
            thread = await AssistantUIUsecase.get_thread(thread_id, user_id)
            
            # Check if messages attribute exists
            if not hasattr(thread, "messages"):
                logger.error(f"Thread {thread_id} has no messages attribute")
                return {"messages": []}
                
            # Return the messages
            messages = thread.messages
            
            # Ensure messages is a list
            if not isinstance(messages, list):
                logger.error(f"Thread {thread_id} messages is not a list: {type(messages)}")
                return {"messages": []}
                
            return {"messages": messages}
        except ValueError as e:
            # Re-raise ValueError for HTTP-specific handling in the route
            raise e
        except Exception as e:
            logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Error retrieving thread messages: {str(e)}")
    
    @staticmethod
    async def process_chat_request(thread_id: str, content: str, user_id: str, system_message: Optional[str] = None):
        """Process a chat request and stream the response."""
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Get the thread data
            try:
                thread_data = await thread_repository.get_thread(thread_id)
            except Exception as db_error:
                logger.error(f"Database error when getting thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to retrieve thread data: {str(db_error)}")
            
            if not thread_data:
                # Thread doesn't exist, create it
                logger.info(f"Thread {thread_id} not found, creating new thread")
                thread_data = {
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "messages": [],
                    "system_message": system_message or DEFAULT_SYSTEM_MESSAGE,
                    "created_at": int(time.time() * 1000),
                    "updated_at": int(time.time() * 1000),
                    "summary": "New conversation"
                }
                
                # Save the thread
                try:
                    await thread_repository.save_thread(thread_data)
                except Exception as db_error:
                    logger.error(f"Database error when saving new thread {thread_id}: {str(db_error)}")
                    raise ValueError(f"Failed to create new thread: {str(db_error)}")
            
            # Add the user message to the thread
            message_data = {
                "role": "user",
                "content": content,
                "timestamp": int(time.time() * 1000)
            }
            
            # Add the message to the thread
            try:
                await thread_repository.add_message_to_thread(thread_id, message_data)
            except Exception as db_error:
                logger.error(f"Database error when adding message to thread {thread_id}: {str(db_error)}")
                raise ValueError(f"Failed to add message to thread: {str(db_error)}")
            
            # Update the thread data with the new message
            try:
                # If thread_data is a dict, update it with the new messages
                if isinstance(thread_data, dict):
                    thread_data["messages"] = await thread_repository.get_thread_messages(thread_id)
                else:
                    # Otherwise, get the updated thread data
                    thread_data = await thread_repository.get_thread(thread_id)
            except Exception as db_error:
                logger.error(f"Database error when getting thread messages for {thread_id}: {str(db_error)}")
                # Continue with potentially outdated messages rather than failing completely
                logger.warning(f"Continuing with potentially outdated messages for thread {thread_id}")
            
            # Ensure the session repository is initialized
            try:
                session_repo = await assistant_service._get_session_repository()
            except Exception as db_error:
                logger.error(f"Database error when initializing session repository: {str(db_error)}")
                raise ValueError(f"Failed to initialize session repository: {str(db_error)}")
            
            # Stream the response
            # The _stream_message_generator will handle the conversion from ThreadModel to dict
            return AssistantUIUsecase._stream_message_generator(thread_data, content, include_thread_id=True)
        except ValueError as ve:
            # Create a generator that yields a specific error for ValueError
            async def value_error_generator():
                yield ErrorChunk(error=str(ve))
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(value_error_generator())
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Create a generator that yields an error
            async def error_generator():
                yield ErrorChunk(error=f"Error processing chat request: {str(e)}")
                
                # End the stream
                done_chunk = DataChunk(data={"thread_id": thread_id})
                done_chunk.type = "finish-message"
                yield done_chunk
            
            return DataStreamResponse(error_generator())
    
    @staticmethod
    async def list_threads(user_id: str, limit: int = 20, skip: int = 0) -> ThreadListResponse:
        """
        List threads for a user.
        
        Args:
            user_id: The ID of the user
            limit: The maximum number of threads to return
            skip: The number of threads to skip
            
        Returns:
            A ThreadListResponse with the threads
        """
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # Get the threads
        threads = await thread_repository.list_threads_by_user(user_id, limit, skip)
        
        return ThreadListResponse(threads=threads)
    
    @staticmethod
    def _stream_message_generator(thread_data: Dict[str, Any], content: str, include_thread_id: bool = False):
        """Generate streaming response for assistant-ui messages using thread data."""
        async def event_generator():
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Convert Pydantic model to dict if needed
            thread_data_dict = thread_data
            if hasattr(thread_data, "model_dump"):
                # It's a Pydantic model, convert to dict
                thread_data_dict = thread_data.model_dump()
            elif not isinstance(thread_data, dict):
                # It's some other object, try to convert to dict
                try:
                    thread_data_dict = dict(thread_data)
                except Exception:
                    # If conversion fails, create a minimal dict with what we can extract
                    thread_data_dict = {}
                    if hasattr(thread_data, "thread_id"):
                        thread_data_dict["thread_id"] = thread_data.thread_id
                    if hasattr(thread_data, "user_id"):
                        thread_data_dict["user_id"] = thread_data.user_id
                    if hasattr(thread_data, "messages"):
                        thread_data_dict["messages"] = thread_data.messages
                    if hasattr(thread_data, "system_message"):
                        thread_data_dict["system_message"] = thread_data.system_message
            
            # Extract thread_id early to ensure it's available in exception blocks
            thread_id = thread_data_dict.get("thread_id", "unknown")
            user_id = thread_data_dict.get("user_id", "unknown")
            
            try:
                message_id = f"msg_{int(time.time() * 1000)}"
                # Use integer milliseconds for timestamp (JavaScript style)
                timestamp = int(time.time() * 1000)
                
                # Start with an empty message in the assistant-ui format
                initial_message = {
                    "id": message_id,
                    "role": "assistant",
                    "content": "",
                    "createdAt": timestamp
                }
                
                # Add thread_id to initial message if requested
                if include_thread_id:
                    initial_message["thread_id"] = thread_id
                
                # Use DataChunk with data in constructor
                yield DataChunk(data=initial_message)
                
                # Ensure the assistant service has the latest state by initializing it with the thread data
                try:
                    # First, check if the session exists in the assistant service
                    session_repo = await assistant_service._get_session_repository()
                    session_state = await session_repo.get_session(thread_id)
                    
                    if not session_state:
                        # Session doesn't exist in the assistant service, create it
                        logger.info(f"Initializing assistant service state for thread {thread_id}")
                        
                        # Create initial state
                        system_message = thread_data_dict.get("system_message")
                        initial_state = create_initial_state("default", system_message)
                        
                        # Add all messages from the thread data
                        messages = thread_data_dict.get("messages", [])
                        for msg in messages:
                            # Handle both dict and object messages
                            if isinstance(msg, dict):
                                role = msg.get("role")
                                msg_content = msg.get("content")
                            else:
                                role = getattr(msg, "role", None)
                                msg_content = getattr(msg, "content", None)
                                
                            if role and msg_content:
                                initial_state["messages"].append({
                                    "role": role,
                                    "content": msg_content
                                })
                        
                        # Save the state to the repository
                        await session_repo.save_session(thread_id, initial_state)
                except Exception as e:
                    logger.error(f"Error initializing assistant service state: {str(e)}")
                    yield ErrorChunk(error=f"Error initializing assistant service: {str(e)}")
                    return
                
                # Stream the message
                try:
                    current_content = ""
                    async for chunk in assistant_service.stream_message(thread_id, content):
                        if "error" in chunk:
                            # Create an error chunk directly with the error message
                            error_msg = chunk.get("error", "Unknown error")
                            logger.error(f"Error from assistant service: {error_msg}")
                            yield ErrorChunk(error=error_msg)
                            break
                        
                        if not chunk.get("messages") or len(chunk.get("messages", [])) == 0:
                            continue
                            
                        # Get the latest content and append to our accumulated content
                        latest_content = chunk["messages"][-1]["content"] if chunk["messages"] else ""
                        if latest_content and latest_content != current_content:
                            # Get just the new text since the last update
                            new_text = latest_content[len(current_content):]
                            current_content = latest_content
                            timestamp = int(time.time() * 1000)  # Update timestamp
                            
                            # Stream the text delta (new text only)
                            yield TextDeltaChunk(text_delta=new_text)
                            
                            # Also send a formatted Data message with the full accumulated content
                            formatted_chunk = {
                                "id": message_id,
                                "role": "assistant",
                                "content": current_content,
                                "createdAt": timestamp
                            }
                            
                            # Add thread_id to formatted chunk if requested
                            if include_thread_id:
                                formatted_chunk["thread_id"] = thread_id
                            
                            # Use DataChunk directly with data in constructor
                            yield DataChunk(data=formatted_chunk)
                except Exception as e:
                    logger.error(f"Error streaming message: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    yield ErrorChunk(error=f"Error streaming message: {str(e)}")
                    return
                
                # Signal the end of the stream with a special data chunk for "done"
                done_chunk = DataChunk(data={})
                if include_thread_id:
                    done_chunk.data = {"thread_id": thread_id}
                done_chunk.type = "finish-message"
                yield done_chunk
                
                # Save the assistant message to MongoDB
                if current_content:
                    try:
                        # Get the thread repository
                        thread_repository = AssistantUIUsecase._get_thread_repository()
                        
                        # Add the assistant message to the thread
                        message_data = {
                            "role": "assistant",
                            "content": current_content,
                            "timestamp": timestamp
                        }
                        
                        # Add the message to the thread
                        asyncio.create_task(thread_repository.add_message_to_thread(thread_id, message_data))
                        
                        # Generate a summary from the conversation
                        summary = current_content[:100] + "..."
                        asyncio.create_task(thread_repository.update_thread_summary(thread_id, summary))
                    except Exception as e:
                        logger.error(f"Error saving assistant message to MongoDB: {str(e)}")
                        # Continue anyway, as the message has already been streamed to the client
                
                logger.info(f"Completed streaming response for thread {thread_id}")
            except (CancelledExc, asyncio.CancelledError) as e:
                # Client disconnected, log and exit gracefully
                logger.info(f"Stream cancelled for thread {thread_id}: {str(e)}")
                # No need to yield anything as the client is gone
            except Exception as e:
                import traceback
                logger.error(f"Error streaming response for thread {thread_id}: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Use ErrorChunk directly with error message in constructor
                yield ErrorChunk(error=str(e))
                
                # Still need to end the stream
                done_chunk = DataChunk(data={})
                if include_thread_id:
                    done_chunk.data = {"thread_id": thread_id}
                done_chunk.type = "finish-message"
                yield done_chunk
        
        return DataStreamResponse(event_generator()) 