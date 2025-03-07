"""
Assistant UI usecase for handling assistant-ui related business logic.
"""
import logging
import asyncio
import time
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
    ChatMessage
)
from src.infrastructure.ai.langgraph.assistant_service import assistant_service

logger = logging.getLogger(__name__)

class AssistantUIUsecase:
    """Usecase class for assistant-ui related operations."""
    
    @staticmethod
    def process_chat_request(chat_request: ChatRequest) -> Dict[str, Any]:
        """Process a chat request from assistant-ui."""
        # Extract the last user message
        last_message = chat_request.messages[-1] if chat_request.messages else None
        
        if not last_message or last_message.role != "user":
            return {"error": "Last message must be from user"}
        
        # Check if we have a thread ID
        thread_id = chat_request.thread_id
        
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
        
        return {
            "thread_id": thread_id,
            "content": last_message_content
        }
    
    @staticmethod
    def stream_message_generator(thread_id: str, content: str):
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
                        
                        # Use DataChunk directly with data in constructor
                        yield DataChunk(data=formatted_chunk)
                
                # Signal the end of the stream with a special data chunk for "done"
                done_chunk = DataChunk(data={})
                done_chunk.type = "finish-message"
                yield done_chunk
                
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
                done_chunk.type = "finish-message"
                yield done_chunk
        
        return DataStreamResponse(event_generator()) 