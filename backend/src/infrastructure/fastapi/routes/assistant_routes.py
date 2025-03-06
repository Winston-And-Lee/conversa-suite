"""
Routes for assistant API integration.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import StreamingResponse
import json
import logging
import asyncio
import time
from anyio import get_cancelled_exc_class

# Import from the assistant_stream package instead of our custom utilities
from assistant_stream import (
    AssistantStreamResponse,
)
from assistant_stream.assistant_stream_chunk import (
    TextDeltaChunk,
    DataChunk, 
    ErrorChunk
)
from assistant_stream.serialization.data_stream import DataStreamEncoder, DataStreamResponse

from src.domain.entity.assistant import (
    CreateThreadRequest,
    CreateThreadResponse,
    SendMessageRequest,
    AssistantMessage,
    SendMessageResponse
)
from src.infrastructure.ai.langgraph.assistant_service import assistant_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])

# No longer need this class as we're using the assistant-stream package
# class AssistantStreamChunkType:
#     TextDelta = "0"  # For streaming text content
#     Data = "2"      # For data objects
#     Error = "3"     # For errors
#     FinishMessage = "d"  # To indicate the end of a message


@router.post("/threads", response_model=CreateThreadResponse)
async def create_thread(request: CreateThreadRequest):
    """Create a new thread."""
    thread_id = assistant_service.create_thread(
        system_message=request.system_message,
        assistant_id=request.assistant_id
    )
    return CreateThreadResponse(thread_id=thread_id)


@router.post("/threads/{thread_id}/messages", response_model=SendMessageResponse)
async def send_message(thread_id: str, request: SendMessageRequest):
    """Send a message to the thread and get a response."""
    if request.stream:
        # Stream the response
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
                async for chunk in assistant_service.stream_message(thread_id, request.content):
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
        
        # Use DataStreamResponse from assistant_stream package
        return DataStreamResponse(event_generator())
    else:
        # Non-streaming response
        try:
            result = await assistant_service.send_message(thread_id, request.content)
            
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            
            return SendMessageResponse(
                thread_id=thread_id,
                messages=result["messages"]
            )
        except Exception as e:
            logger.error(f"Error sending message to thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/messages", response_model=SendMessageResponse)
async def get_thread_messages(thread_id: str):
    """Get the message history for a thread."""
    try:
        messages = assistant_service.get_thread_messages(thread_id)
        
        if not messages and thread_id:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return SendMessageResponse(
            thread_id=thread_id,
            messages=messages
        )
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread."""
    try:
        success = assistant_service.delete_thread(thread_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return {"message": "Thread deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 