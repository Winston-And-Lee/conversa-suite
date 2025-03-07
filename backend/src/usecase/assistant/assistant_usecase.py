"""
Assistant usecase for handling assistant-related business logic.
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
    CreateThreadRequest,
    CreateThreadResponse,
    SendMessageRequest,
    SendMessageResponse
)
from src.infrastructure.ai.langgraph.assistant_service import assistant_service

logger = logging.getLogger(__name__)

class AssistantUsecase:
    """Usecase class for assistant-related operations."""
    
    @staticmethod
    def create_thread(request: CreateThreadRequest) -> CreateThreadResponse:
        """Create a new assistant thread."""
        thread_id = assistant_service.create_thread(
            system_message=request.system_message,
            assistant_id=request.assistant_id
        )
        return CreateThreadResponse(thread_id=thread_id)
    
    @staticmethod
    async def send_message(thread_id: str, request: SendMessageRequest) -> Dict[str, Any]:
        """Send a message to the assistant and get a response."""
        try:
            # Non-streaming response
            result = await assistant_service.send_message(thread_id, request.content)
            
            if "error" in result:
                return {"error": result["error"]}
            
            return SendMessageResponse(
                thread_id=thread_id,
                messages=result["messages"]
            )
        except Exception as e:
            logger.error(f"Error sending message to thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    @staticmethod
    def stream_message_generator(thread_id: str, content: str):
        """Generate streaming response for assistant messages."""
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
                
                # Use DataChunk instead of the custom wrapper
                initial_chunk = DataChunk()
                initial_chunk.data = initial_message
                yield initial_chunk
                
                current_content = ""
                async for chunk in assistant_service.stream_message(thread_id, content):
                    if "error" in chunk:
                        # Use ErrorChunk directly
                        error_chunk = ErrorChunk()
                        error_chunk.error = chunk["error"]
                        yield error_chunk
                        break
                    
                    # Get the content from the chunk
                    if "messages" in chunk and chunk["messages"] and len(chunk["messages"]) > 0:
                        latest_message = chunk["messages"][-1]
                        if latest_message["role"] == "assistant" and latest_message["content"] != current_content:
                            # Get just the new text since the last update
                            new_text = latest_message["content"][len(current_content):]
                            current_content = latest_message["content"]
                            timestamp = int(time.time() * 1000)  # Update timestamp
                            
                            # Stream the text delta (new text only)
                            text_delta = TextDeltaChunk()
                            text_delta.text_delta = new_text
                            yield text_delta
                            
                            # Also send a formatted Data message with the full accumulated content
                            formatted_chunk = {
                                "id": message_id,
                                "role": "assistant",
                                "content": current_content,
                                "createdAt": timestamp
                            }
                            
                            # Use DataChunk directly
                            data_chunk = DataChunk()
                            data_chunk.data = formatted_chunk
                            yield data_chunk
                
                # Signal the end of the stream with a special data chunk for "done"
                done_chunk = DataChunk()
                done_chunk.data = {}
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
                
                # Use ErrorChunk directly
                error_chunk = ErrorChunk()
                error_chunk.error = str(e)
                yield error_chunk
                
                # Still need to end the stream
                done_chunk = DataChunk()
                done_chunk.data = {}
                done_chunk.type = "finish-message"
                yield done_chunk
        
        return DataStreamResponse(event_generator())
    
    @staticmethod
    def get_thread_messages(thread_id: str) -> SendMessageResponse:
        """Get the message history for a thread."""
        messages = assistant_service.get_thread_messages(thread_id)
        
        return SendMessageResponse(
            thread_id=thread_id,
            messages=messages
        )
    
    @staticmethod
    def delete_thread(thread_id: str) -> bool:
        """Delete an assistant thread."""
        return assistant_service.delete_thread(thread_id) 