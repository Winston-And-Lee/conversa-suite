"""
Assistant implementation using LangGraph to support the assistant-ui format.
"""
import logging
import uuid
from typing import Dict, List, Any, TypedDict, Optional, Annotated, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from ..model import create_llm, create_chat_prompt
from ..config import ASSISTANT_ID

logger = logging.getLogger(__name__)

# Define the state structure for assistant-ui
class AssistantUIState(TypedDict, total=False):
    """State for the assistant-ui graph."""
    messages: List[Dict[str, str]]  # List of messages in the format {role: "user"|"assistant"|"system", content: string}
    tools: Dict[str, Any]  # Tools available to the assistant
    metadata: Dict[str, Any]  # Metadata for tracing and context

def create_assistant_ui_agent():
    """Create a LangGraph agent that supports the assistant-ui format."""
    try:
        # Create the language model
        llm = create_llm(
            run_name="Conversa Suite Assistant",
            metadata={"agent_type": "assistant-ui", "framework": "langgraph"}
        )
        
        # Define the graph
        workflow = StateGraph(AssistantUIState)
        
        # Define the node that processes messages
        def process_message(state: AssistantUIState) -> AssistantUIState:
            """Process messages and generate a response."""
            # Extract the last user message
            messages = state.get("messages", [])
            if not messages:
                return state
            
            # Convert messages to LangChain format
            lc_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
            
            # Get response from LLM
            response = llm.invoke(lc_messages)
            
            # Add assistant's response to the messages
            state["messages"].append({
                "role": "assistant",
                "content": response.content
            })
            
            return state
        
        # Add nodes to the graph
        workflow.add_node("process_message", process_message)
        
        # Define edges
        workflow.add_edge("process_message", END)
        
        # Set the entry point
        workflow.set_entry_point("process_message")
        
        # Compile the graph
        compiled_graph = workflow.compile()
        
        logger.info("Assistant-UI agent created successfully")
        return compiled_graph
    except Exception as e:
        logger.error(f"Error creating assistant-ui agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Create a fallback agent
        def fallback_agent(state: AssistantUIState) -> AssistantUIState:
            state["messages"].append({
                "role": "assistant",
                "content": "I apologize, but I'm experiencing technical difficulties. Please try again later."
            })
            return state
        
        # Return a minimal placeholder graph
        workflow = StateGraph(AssistantUIState)
        workflow.add_node("fallback", fallback_agent)
        workflow.add_edge("fallback", END)
        workflow.set_entry_point("fallback")
        logger.info("Created fallback assistant-ui agent due to errors")
        return workflow.compile()

def create_initial_state(assistant_id: Optional[str] = None, system_message: Optional[str] = None) -> AssistantUIState:
    """Create the initial state for the assistant-ui graph."""
    messages = []
    
    # Add system message if provided
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    return {
        "messages": messages,
        "tools": {},
        "metadata": {
            "assistant_id": assistant_id or ASSISTANT_ID,
            "session_id": str(uuid.uuid4())
        }
    } 