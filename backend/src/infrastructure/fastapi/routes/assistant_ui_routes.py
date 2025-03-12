"""
Routes for assistant-ui chat integration.
"""
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Request, Depends, Query
import json
import time
import logging
import asyncio
import anyio
from anyio import get_cancelled_exc_class
from pydantic import BaseModel, Field

from src.domain.entity.assistant import (
    ContentPart,
    ChatMessage,
    ChatRequest,
    ThreadListResponse
)
from src.usecase import AssistantUIUsecase
from src.infrastructure.fastapi.routes.user_routes import get_current_user
from src.domain.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["assistant-ui"])

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
        
        # Stream the response
        return AssistantUIUsecase.stream_message_generator(
            result["thread_id"], 
            result["content"],
            user_id=current_user.id
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