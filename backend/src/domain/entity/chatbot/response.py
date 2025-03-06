"""
Response entity models for the chatbot.
"""
from typing import Dict, List
from pydantic import BaseModel


class ChatSessionResponse(BaseModel):
    """Response model for chat session creation."""
    session_id: str


class ChatMessageRequest(BaseModel):
    """Request model for sending chat messages."""
    message: str


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    session_id: str
    response: str
    messages: List[Dict[str, str]]


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    messages: List[Dict[str, str]] 