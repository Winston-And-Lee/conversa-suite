"""
Domain entities for assistant and assistant-ui functionality.
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

# =============================================
# Assistant Models
# =============================================

class CreateThreadRequest(BaseModel):
    """Request model for creating a new thread."""
    system_message: Optional[str] = None
    assistant_id: Optional[str] = None


class CreateThreadResponse(BaseModel):
    """Response model for thread creation."""
    thread_id: str


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    content: str
    stream: bool = False


class AssistantMessage(BaseModel):
    """Model for assistant message."""
    role: str
    content: str


class SendMessageResponse(BaseModel):
    """Response model for message sending."""
    thread_id: str
    messages: List[Dict[str, str]]


# =============================================
# Assistant UI Models
# =============================================

class ContentPart(BaseModel):
    """Model for a content part in a message."""
    type: str
    text: Optional[str] = None


class ChatMessage(BaseModel):
    """Model for chat message."""
    role: str
    content: Union[str, List[Dict[str, Any]]]  # Can be a string or a list of content parts
    id: Optional[str] = None
    createdAt: Optional[Union[float, str]] = None
    
    def get_content_text(self) -> str:
        """Extract text from content field, handling different formats."""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, list):
            # Extract text from all content parts
            result = ""
            for part in self.content:
                if isinstance(part, dict):
                    if part.get("type") == "text" and "text" in part:
                        result += part["text"]
            return result
        return ""


class ChatRequest(BaseModel):
    """Request model for chat."""
    messages: List[ChatMessage]
    system: Optional[str] = None
    tools: Optional[Union[Dict[str, Any], List[Any]]] = None  # Can be dict or list
    thread_id: Optional[str] = None
    # Add additional fields for flexibility
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = True 