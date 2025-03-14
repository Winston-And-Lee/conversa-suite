"""
Entity module for domain entities.

This module contains entity classes that represent domain concepts.
"""

from src.domain.entity.user import (
    UserCreate,
    AuthResponse,
    RefreshTokenResponse,
    VerificationRequestResponse,
    VerificationResponse,
    ProfileResponse,
    PasswordResetResponse
)

from src.domain.entity.chatbot import (
    ChatSessionResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse
)

from src.domain.entity.assistant import (
    # Assistant models
    CreateThreadRequest,
    CreateThreadResponse,
    SendMessageRequest,
    SendMessageResponse,
    
    # Assistant UI models
    ContentPart,
    ChatMessage,
    ChatRequest
)

from src.domain.entity.common import StandardizedResponse, get_schema_field

__all__ = [
    # User entities
    "UserCreate",
    "AuthResponse",
    "RefreshTokenResponse",
    "VerificationRequestResponse",
    "VerificationResponse",
    "ProfileResponse",
    "PasswordResetResponse",
    
    # Chatbot entities
    "ChatSessionResponse",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    
    # Assistant entities
    "CreateThreadRequest",
    "CreateThreadResponse",
    "SendMessageRequest",
    "SendMessageResponse",
    
    # Assistant UI entities
    "ContentPart",
    "ChatMessage",
    "ChatRequest",
    "StandardizedResponse",
    "get_schema_field"
]
