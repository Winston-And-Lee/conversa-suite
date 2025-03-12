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
from src.infrastructure.ai.langgraph.assistant_service import assistant_service, assistant_sessions
from src.interface.repository.mongodb.thread_repository import MongoDBThreadRepository
from src.infrastructure.ai.langgraph.assistant import create_initial_state

logger = logging.getLogger(__name__)

class AssistantUIUsecase:
    """Usecase class for assistant-ui related operations."""
    
    @staticmethod
    def _get_thread_repository():
        """Get the thread repository."""
        return MongoDBThreadRepository()
    
    @staticmethod
    async def create_thread(content: str, user_id: str) -> str:
        """
        Create a new thread with an initial message.
        
        Args:
            content: The initial message content
            user_id: The ID of the user creating the thread
            
        Returns:
            The ID of the created thread
        """
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Create a new thread with UUID
            thread_id = str(uuid.uuid4())
            
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
            await thread_repository.create_thread(thread_data)
            
            # Initialize state in assistant_service
            initial_state = create_initial_state("default", thread_data.get("system_message"))
            
            # Add the user message to the assistant_service's session
            initial_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Store the state in the assistant_service's sessions
            assistant_sessions[thread_id] = initial_state
            
            logger.info(f"Created new thread {thread_id} for user {user_id}")
            
            return thread_id
            
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise e
    
    @staticmethod
    async def add_message_to_thread(thread_id: str, content: str, user_id: str) -> None:
        """
        Add a message to an existing thread.
        
        Args:
            thread_id: The ID of the thread
            content: The message content
            user_id: The ID of the user adding the message
            
        Raises:
            ValueError: If the thread is not found or the user doesn't have permission
        """
        try:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Get the thread
            thread = await thread_repository.get_thread(thread_id)
            
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
            await thread_repository.add_message_to_thread(thread_id, message_data)
            
            # Update the summary
            await thread_repository.update_thread_summary(thread_id, content[:100] + "..." if len(content) > 100 else content)
            
            # Ensure assistant_service has the thread initialized with all messages from MongoDB
            # Check if the thread exists in the assistant_service
            if thread_id not in assistant_sessions:
                # Thread doesn't exist in assistant_service's memory, create it and populate with messages from MongoDB
                # Initialize state in assistant_service
                initial_state = create_initial_state("default", thread.system_message)
                
                # Add all messages from MongoDB
                for msg in thread.messages:
                    initial_state["messages"].append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # Store in assistant_sessions
                assistant_sessions[thread_id] = initial_state
                logger.info(f"Loaded thread {thread_id} from MongoDB into assistant_service with {len(thread.messages)} messages")
            else:
                # Thread exists, but ensure the message we just added is in the assistant_service
                assistant_sessions[thread_id]["messages"].append({
                    "role": "user",
                    "content": content
                })
            
            logger.info(f"Added message to thread {thread_id} for user {user_id}")
            
        except ValueError as e:
            # Re-raise ValueError for HTTP-specific handling in the route
            raise e
        except Exception as e:
            logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
            raise e
    
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
            thread = await thread_repository.get_thread(thread_id)
            
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            
            # Check if the thread belongs to the current user
            if thread.user_id != user_id:
                raise ValueError("You don't have permission to access this thread")
            
            return thread
        except ValueError as e:
            # Re-raise ValueError for HTTP-specific handling in the route
            raise e
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def get_thread_messages(thread_id: str, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get messages for a specific thread.
        
        Args:
            thread_id: The ID of the thread to get messages for
            user_id: The ID of the user requesting the messages
            
        Returns:
            A dictionary containing the messages for the thread
            
        Raises:
            ValueError: If the thread is not found or the user doesn't have permission
        """
        try:
            # Get the thread
            thread = await AssistantUIUsecase.get_thread(thread_id, user_id)
            
            # Return the messages
            return {"messages": thread.messages}
        except ValueError as e:
            # Re-raise ValueError for HTTP-specific handling in the route
            raise e
        except Exception as e:
            logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
            raise e
    
    @staticmethod
    async def process_chat_request(chat_request: ChatRequest, user_id: Optional[str] = None, skip_message_add: bool = False) -> Dict[str, Any]:
        """Process a chat request from assistant-ui."""
        # Extract the last user message
        last_message = chat_request.messages[-1] if chat_request.messages else None
        
        if not last_message or last_message.role != "user":
            return {"error": "Last message must be from user"}
        
        # Check if we have a thread ID
        thread_id = chat_request.thread_id
        is_new_thread = not thread_id
        
        if not thread_id:
            # Create a new thread
            thread_id = assistant_service.create_thread(
                system_message=chat_request.system,
                assistant_id="default"
            )
            
            # Initialize with system message if provided
            # The system message is already added by create_thread
            
            # Add previous messages to the thread (excluding the last one)
            for msg in chat_request.messages[:-1]:
                assistant_service.get_thread_messages(thread_id).append({
                    "role": msg.role,
                    "content": msg.get_content_text()
                })
        
        # Get the text content from the last message
        last_message_content = last_message.get_content_text()
        logger.info(f"Processing message for thread {thread_id}: {last_message_content[:50]}...")
        
        # If user_id is provided, save the thread to MongoDB
        if user_id:
            # Get the thread repository
            thread_repository = AssistantUIUsecase._get_thread_repository()
            
            # Check if the thread exists in MongoDB
            thread = await thread_repository.get_thread(thread_id)
            
            if not thread and is_new_thread:
                # Create a new thread in MongoDB
                thread_data = {
                    "thread_id": thread_id,
                    "user_id": user_id,
                    "title": f"Chat {int(time.time())}",  # Default title
                    "summary": last_message_content[:100] + "...",  # Initial summary
                    "messages": [],
                    "system_message": chat_request.system,
                    "is_archived": False
                }
                
                # Add messages to the thread data
                for msg in chat_request.messages:
                    # Skip adding messages if specified (to avoid duplicates when thread was already created)
                    if skip_message_add and msg == last_message:
                        logger.info(f"Skipping addition of message that was already added to thread {thread_id}")
                        continue
                    
                    thread_data["messages"].append({
                        "role": msg.role,
                        "content": msg.get_content_text(),
                        "timestamp": int(time.time() * 1000)
                    })
                
                # Create the thread in MongoDB
                await thread_repository.create_thread(thread_data)
            elif thread:
                # Only add the message to the existing thread if not skipping
                if not skip_message_add:
                    # Add the message to the existing thread
                    message_data = {
                        "role": last_message.role,
                        "content": last_message_content,
                        "timestamp": int(time.time() * 1000)
                    }
                    
                    # Add the message to the thread
                    await thread_repository.add_message_to_thread(thread_id, message_data)
                
                # Always update the summary
                await thread_repository.update_thread_summary(thread_id, last_message_content[:100] + "...")
        
        return {
            "thread_id": thread_id,
            "content": last_message_content
        }
    
    @staticmethod
    async def list_threads(user_id: str, limit: int = 20, skip: int = 0) -> ThreadListResponse:
        """
        List threads for a user.
        
        Args:
            user_id: The ID of the user
            limit: The maximum number of threads to return
            skip: The number of threads to skip
            
        Returns:
            A list of threads
        """
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # List threads for the user
        threads = await thread_repository.list_threads_by_user(user_id, limit, skip)
        
        return ThreadListResponse(threads=threads)
    
    @staticmethod
    def stream_message_generator(thread_id: str, content: str, user_id: Optional[str] = None, include_thread_id: bool = False):
        """Generate streaming response for assistant-ui messages."""
        async def event_generator():
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
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
                
                current_content = ""
                async for chunk in assistant_service.stream_message(thread_id, content):
                    if "error" in chunk:
                        # Create an error chunk directly with the error message
                        yield ErrorChunk(error=chunk["error"])
                        break
                    
                    if not chunk["messages"] or len(chunk["messages"]) == 0:
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
                
                # Signal the end of the stream with a special data chunk for "done"
                done_chunk = DataChunk(data={})
                if include_thread_id:
                    done_chunk.data = {"thread_id": thread_id}
                done_chunk.type = "finish-message"
                yield done_chunk
                
                # If user_id is provided, save the assistant message to MongoDB
                if user_id and current_content:
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
                
                logger.info(f"Completed streaming response for thread {thread_id}")
            except (CancelledExc, asyncio.CancelledError) as e:
                # Client disconnected, log and exit gracefully
                logger.info(f"Stream cancelled for thread {thread_id}: {str(e)}")
                # No need to yield anything as the client is gone
            except Exception as e:
                import traceback
                traceback.print_exc()
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