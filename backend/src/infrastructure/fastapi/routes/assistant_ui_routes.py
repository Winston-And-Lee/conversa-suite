"""
Routes for assistant-ui chat integration.
"""
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Request, Depends, Query, Body
import json
import time
import logging
import asyncio
import anyio
from anyio import get_cancelled_exc_class
from pydantic import BaseModel, Field
import uuid  # Add import for uuid module

from src.domain.entity.assistant import (
    ContentPart,
    ChatMessage,
    ChatRequest,
    ThreadListResponse
)
from src.usecase.assistant.assistant_ui_usecase import AssistantUIUsecase
from src.infrastructure.fastapi.routes.user_routes import get_current_user
from src.domain.models.user import User
from src.domain.models.thread import ThreadModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["assistant-ui"])

class MessageRequest(BaseModel):
    """Request model for sending a message."""
    content: str

@router.post("/threads")
async def create_thread(
    request: MessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new thread with an initial message.
    
    Args:
        request: The message request
        current_user: The current authenticated user
        
    Returns:
        A streaming response with the AI's reply
    """
    try:
        # Create a new thread and stream response using the usecase
        return await AssistantUIUsecase.create_thread_and_stream_response(
            content=request.content,
            user_id=current_user.id
        )
        
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/threads/{thread_id}/messages")
async def add_message_to_thread(
    thread_id: str,
    request: MessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to an existing thread.
    
    Args:
        thread_id: The ID of the thread
        request: The message request
        current_user: The current authenticated user
        
    Returns:
        A streaming response with the AI's reply
    """
    try:
        # Add message to thread and stream response using the usecase
        return await AssistantUIUsecase.add_message_and_stream_response(
            thread_id=thread_id,
            content=request.content,
            user_id=current_user.id
        )
        
    except ValueError as e:
        # Handle specific value errors with appropriate HTTP status codes
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "permission" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: Request, current_user: User = Depends(get_current_user)):
    """Chat endpoint for assistant-ui integration."""
    try:
        # Parse the raw request to handle various formats
        raw_body = await request.json()
        logger.debug(f"Received request: {json.dumps(raw_body)}")
        
        # Create a ChatRequest from the raw data
        try:
            chat_request = ChatRequest(**raw_body)
        except Exception as e:
            logger.error(f"Error parsing request: {e}")
            logger.error(f"Raw request: {json.dumps(raw_body)}")
            raise HTTPException(status_code=422, detail=f"Invalid request format: {str(e)}")
            
        # Process the chat request using the usecase
        result = await AssistantUIUsecase.process_chat_request(chat_request, user_id=current_user.id)
        
        if "error" in result:
            return HTTPException(status_code=400, detail=result["error"])
        
        # Get the thread data
        thread = await AssistantUIUsecase.get_thread(result["thread_id"], current_user.id)
        
        # Stream the response
        return AssistantUIUsecase._stream_message_generator(
            thread_data=thread,
            content=result["content"],
            include_thread_id=True
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    List threads for the current user.
    
    Args:
        limit: The maximum number of threads to return
        skip: The number of threads to skip
        current_user: The current authenticated user
        
    Returns:
        A list of threads
    """
    try:
        return await AssistantUIUsecase.list_threads(current_user.id, limit, skip)
    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}", response_model=ThreadModel)
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific thread with its messages.
    
    Args:
        thread_id: The ID of the thread to get
        current_user: The current authenticated user
        
    Returns:
        The thread with its messages
    """
    try:
        return await AssistantUIUsecase.get_thread(thread_id, current_user.id)
    except ValueError as e:
        # Handle specific value errors with appropriate HTTP status codes
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "permission" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get messages for a specific thread.
    
    Args:
        thread_id: The ID of the thread to get messages for
        current_user: The current authenticated user
        
    Returns:
        The messages for the thread
    """
    try:
        return await AssistantUIUsecase.get_thread_messages(thread_id, current_user.id)
    except ValueError as e:
        # Handle specific value errors with appropriate HTTP status codes
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "permission" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 