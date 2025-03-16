"""
LangGraph agent configuration for the conversational AI.
"""
import logging
from typing import Dict, List, Tuple, Any, TypedDict, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# Import with error handling
try:
    from langgraph.prebuilt import create_react_agent
except ImportError:
    # Fallback for compatibility
    logging.error("Could not import create_react_agent from langgraph.prebuilt")
    # Create a placeholder function that returns an identity function
    def create_react_agent(llm, tools):
        return lambda x: {"messages": x.get("messages", []) + [{"role": "assistant", "content": "Sorry, I'm having technical difficulties."}]}

from .model import create_llm, format_chat_history
from ..config import ASSISTANT_ID

logger = logging.getLogger(__name__)

# Define the state structure
class ChatState(TypedDict, total=False):
    """State for the chat agent graph."""
    messages: List[Dict[str, str]]
    chat_history: List[BaseMessage]
    assistant_id: str
    _metadata: Dict[str, Any]  # Optional metadata for tracing
    _run_name: str  # Optional run name for tracing

def create_chat_agent():
    """Create a conversational agent using LangGraph."""
    try:
        # Create the language model with default settings
        # The actual metadata will be provided at runtime from the service
        llm = create_llm(
            run_name="Conversa Suite Chatbot",
            metadata={"agent_type": "chat", "framework": "langgraph"}
        )
        
        # Create a simple ReAct agent
        agent_executor = create_react_agent(llm, [])
        
        # Define the graph
        workflow = StateGraph(ChatState)
        
        # Define the nodes
        workflow.add_node("agent", agent_executor)
        
        # Define edges - for simple chatbot, we go directly to END after agent responds
        workflow.add_edge("agent", END)
        
        # Set the entry point
        workflow.set_entry_point("agent")
        
        # Compile the graph
        compiled_graph = workflow.compile()
        
        logger.info("Chat agent created successfully")
        return compiled_graph
    except Exception as e:
        logger.error(f"Error creating chat agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Create a fallback agent that always returns a simple response
        def fallback_agent(state: ChatState) -> ChatState:
            state["messages"].append({
                "role": "assistant",
                "content": "I apologize, but I'm experiencing technical difficulties. Please try again later."
            })
            return state
        
        # Return a minimal placeholder graph
        workflow = StateGraph(ChatState)
        workflow.add_node("agent", fallback_agent)
        workflow.add_edge("agent", END)
        workflow.set_entry_point("agent")
        logger.info("Created fallback agent due to errors")
        return workflow.compile()

def process_input(state: ChatState, user_input: str) -> ChatState:
    """Process user input and update the state."""
    # Add the user message to the messages list
    state["messages"].append({
        "role": "user",
        "content": user_input
    })
    
    # Update the chat history for the LLM
    try:
        state["chat_history"] = format_chat_history(state["messages"])
    except Exception as e:
        logger.error(f"Error formatting chat history: {str(e)}")
        # Ensure chat_history is at least an empty list
        state["chat_history"] = []
    
    return state

def create_initial_state(assistant_id: Optional[str] = None) -> ChatState:
    """Create the initial state for the graph."""
    return {
        "messages": [],
        "chat_history": [],
        "assistant_id": assistant_id or ASSISTANT_ID
    } 