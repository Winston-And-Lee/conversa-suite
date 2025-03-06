"""
Routes for chatbot functionality.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException

from src.domain.entity.chatbot import (
    ChatSessionResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse
)
from src.infrastructure.ai.langgraph.service import chatbot_service, chat_sessions

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(assistant_id: Optional[str] = None):
    """Create a new chat session."""
    session_id = chatbot_service.create_session(assistant_id)
    return ChatSessionResponse(session_id=session_id)

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(session_id: str, request: ChatMessageRequest):
    """Send a message to the chatbot and get a response."""
    result = await chatbot_service.send_message(session_id, request.message)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return ChatMessageResponse(
        session_id=session_id,
        response=result["response"],
        messages=result["messages"]
    )

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Get the message history for a chat session."""
    messages = chatbot_service.get_session_history(session_id)
    
    if not messages and session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ChatHistoryResponse(messages=messages)

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session."""
    success = chatbot_service.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

@router.get("/debug/test-message")
async def test_message():
    """Test endpoint for debugging the message sending functionality."""
    try:
        # Create a new session
        session_id = chatbot_service.create_session()
        
        # Send a test message
        result = await chatbot_service.send_message(session_id, "Hello, this is a test message.")
        
        # Return basic information for debugging
        return {
            "success": True,
            "session_id": session_id,
            "result": result
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": error_trace
        } 