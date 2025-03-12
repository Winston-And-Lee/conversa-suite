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
from src.usecase import AssistantUIUsecase
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
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # Create a new thread with UUID
        thread_id = str(uuid.uuid4())
        
        # Create the thread data
        thread_data = {
            "thread_id": thread_id,
            "user_id": current_user.id,
            "title": f"Chat {int(time.time())}",  # Default title
            "summary": request.content[:100] + "..." if len(request.content) > 100 else request.content,
            "messages": [{
                "role": "user",
                "content": request.content,
                "timestamp": int(time.time() * 1000)
            }],
            "system_message": None,
            "is_archived": False
        }
        
        # Create the thread in MongoDB
        await thread_repository.create_thread(thread_data)
        
        # Ensure assistant_service has the thread initialized with the same messages
        from src.infrastructure.ai.langgraph.assistant_service import assistant_service
        from src.infrastructure.ai.langgraph.assistant import create_initial_state
        
        # Initialize state in assistant_service
        initial_state = create_initial_state("default", thread_data.get("system_message"))
        
        # Add the user message to the assistant_service's session
        initial_state["messages"].append({
            "role": "user",
            "content": request.content
        })
        
        # Store the state in the assistant_service's sessions
        from src.infrastructure.ai.langgraph.assistant_service import assistant_sessions
        assistant_sessions[thread_id] = initial_state
        
        logger.info(f"Created new thread {thread_id} for user {current_user.id}")
        
        # Return streaming response directly using assistant_service, with explicit thread_id
        return AssistantUIUsecase.stream_message_generator(
            thread_id,
            request.content,
            user_id=current_user.id,
            include_thread_id=True  # Explicitly include thread_id in response
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
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # Get the thread
        thread = await thread_repository.get_thread(thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
        
        # Check if the thread belongs to the current user
        if thread.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to access this thread")
        
        # Add the message to the thread
        message_data = {
            "role": "user",
            "content": request.content,
            "timestamp": int(time.time() * 1000)
        }
        
        # Add the message to the thread in MongoDB
        await thread_repository.add_message_to_thread(thread_id, message_data)
        
        # Update the summary
        await thread_repository.update_thread_summary(thread_id, request.content[:100] + "..." if len(request.content) > 100 else request.content)
        
        # Ensure assistant_service has the thread initialized with all messages from MongoDB
        from src.infrastructure.ai.langgraph.assistant_service import assistant_service, assistant_sessions
        
        # Check if the thread exists in the assistant_service
        if thread_id not in assistant_sessions:
            # Thread doesn't exist in assistant_service's memory, create it and populate with messages from MongoDB
            from src.infrastructure.ai.langgraph.assistant import create_initial_state
            
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
                "content": request.content
            })
        
        logger.info(f"Added message to thread {thread_id} for user {current_user.id}")
        
        # Return streaming response directly using assistant_service
        return AssistantUIUsecase.stream_message_generator(
            thread_id,
            request.content,
            user_id=current_user.id,
            include_thread_id=True  # Also include thread_id in add_message responses
        )
        
    except HTTPException:
        raise
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
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # Get the thread
        thread = await thread_repository.get_thread(thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
        
        # Check if the thread belongs to the current user
        if thread.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to access this thread")
        
        return thread
    except HTTPException:
        raise
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
        # Get the thread repository
        thread_repository = AssistantUIUsecase._get_thread_repository()
        
        # Get the thread
        thread = await thread_repository.get_thread(thread_id)
        
        if not thread:
            raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
        
        # Check if the thread belongs to the current user
        if thread.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to access this thread")
        
        # Return the messages
        return {"messages": thread.messages}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for thread {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 