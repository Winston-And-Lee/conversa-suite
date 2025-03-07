"""
Routes for assistant-ui chat integration.
"""
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Request
import json
import time
import logging
import asyncio
import anyio
from anyio import get_cancelled_exc_class
from pydantic import BaseModel, Field

#
from assistant_stream.assistant_stream_chunk import (
    TextDeltaChunk,
    DataChunk, 
    ErrorChunk
)
from assistant_stream.serialization.data_stream import DataStreamEncoder, DataStreamResponse

from src.domain.entity.assistant import (
    ContentPart,
    ChatMessage,
    ChatRequest
)
from src.usecase import AssistantUIUsecase

logger = logging.getLogger(__name__)
router = APIRouter(tags=["assistant-ui"])

@router.post("/chat")
async def chat(request: Request):
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
        result = AssistantUIUsecase.process_chat_request(chat_request)
        
        if "error" in result:
            return HTTPException(status_code=400, detail=result["error"])
        
        # Stream the response
        return AssistantUIUsecase.stream_message_generator(result["thread_id"], result["content"])
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 