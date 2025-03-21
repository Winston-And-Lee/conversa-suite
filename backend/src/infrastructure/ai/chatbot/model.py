"""
Language model setup for the chatbot.
"""
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

def create_llm(run_name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, streaming: bool = False):
    """Create and configure the language model."""
    if not OPENAI_API_KEY:
        logger.warning("No OpenAI API key provided. LLM functionality will be limited.")
    
    # Setup for tracing
    callbacks = []
    # Instead of using ConsoleTracer (which isn't available), we'll rely on 
    # the LangSmith tracing that's configured through environment variables
    
    # Initialize the OpenAI chat model
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL,
        temperature=0.7,
        # Only pass callbacks if we have any
        callbacks=callbacks if callbacks else None,
        tags=["conversa-suite", "chatbot"],  # Tags for identifying runs in LangSmith
        metadata=metadata or {},  # Custom metadata for the run
        streaming=streaming,  # Enable streaming if requested
    )
    
    return llm

def format_chat_history(messages):
    """Format a list of message dictionaries into LangChain message objects."""
    formatted_messages = []
    
    for message in messages:
        if message["role"] == "user":
            formatted_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            formatted_messages.append(AIMessage(content=message["content"]))
        elif message["role"] == "system":
            formatted_messages.append(SystemMessage(content=message["content"]))
    
    return formatted_messages 