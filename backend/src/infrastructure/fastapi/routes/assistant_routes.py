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
from src.usecase import AssistantUsecase

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
    return AssistantUsecase.create_thread(request)


@router.post("/threads/{thread_id}/messages", response_model=SendMessageResponse)
async def send_message(thread_id: str, request: SendMessageRequest):
    """Send a message to the thread and get a response."""
    if request.stream:
        # Stream the response
        return AssistantUsecase.stream_message_generator(thread_id, request.content)
    else:
        # Non-streaming response
        try:
            result = await AssistantUsecase.send_message(thread_id, request)
            
            if isinstance(result, dict) and "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error sending message to thread {thread_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads/{thread_id}/messages", response_model=SendMessageResponse)
async def get_thread_messages(thread_id: str):
    """Get the message history for a thread."""
    try:
        result = AssistantUsecase.get_thread_messages(thread_id)
        
        if not result.messages and thread_id:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return result
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread."""
    try:
        success = AssistantUsecase.delete_thread(thread_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return {"message": "Thread deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 