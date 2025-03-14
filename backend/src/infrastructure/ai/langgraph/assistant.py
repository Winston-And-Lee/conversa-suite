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
from src.interface.repository.database.db_repository import pinecone_repository

logger = logging.getLogger(__name__)

# Define the state structure for assistant-ui
class AssistantUIState(TypedDict, total=False):
    """State for the assistant-ui graph."""
    messages: List[Dict[str, str]]  # List of messages in the format {role: "user"|"assistant"|"system", content: string}
    tools: Dict[str, Any]  # Tools available to the assistant
    metadata: Dict[str, Any]  # Metadata for tracing and context
    is_fiction_topic: bool  # Flag to indicate if the topic is about fiction
    pinecone_results: List[Dict[str, Any]]  # Results from Pinecone query

def create_assistant_ui_agent():
    """Create a LangGraph agent that supports the assistant-ui format."""
    try:
        # Create the language model
        llm = create_llm(
            run_name="Conversa Suite Assistant",
            metadata={"agent_type": "assistant-ui", "framework": "langgraph"}
        )
        
        # Initialize Pinecone repository
        pinecone_repo = pinecone_repository()
        
        # Define the graph
        workflow = StateGraph(AssistantUIState)
        
        # Define the node that detects fiction topics
        async def detect_fiction_topic(state: AssistantUIState) -> dict:
            """Detect if the user's message is about fiction and route accordingly."""
            # Extract the last user message
            messages = state.get("messages", [])
            if not messages:
                return {"next": "process_message"}
            
            last_user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
            
            if not last_user_message:
                return {"next": "process_message"}
            
            # Use the LLM to classify if the message is about fiction
            classification_prompt = [
                SystemMessage(content="You are a topic classifier. Determine if the user's message is about fiction (novels, stories, fairy tales, etc.). Respond with only 'YES' if it's about fiction or 'NO' if it's not."),
                HumanMessage(content=last_user_message)
            ]
            
            classification_llm = create_llm(
                run_name="Fiction Topic Classification",
                metadata={"task": "fiction_classification"}
            )
            
            classification_result = classification_llm.invoke(classification_prompt)
            is_fiction = "YES" in classification_result.content.upper()
            
            # Update state with classification result
            state["is_fiction_topic"] = is_fiction
            state["pinecone_results"] = []
            
            # Route based on classification
            if is_fiction:
                logger.info(f"Detected fiction topic in message: {last_user_message[:50]}...")
                return {"next": "query_pinecone"}
            else:
                logger.info(f"Non-fiction topic detected in message: {last_user_message[:50]}...")
                return {"next": "process_message"}
        
        # Define the node that queries Pinecone for fiction-related content
        async def query_pinecone(state: AssistantUIState) -> AssistantUIState:
            """Query Pinecone for fiction-related content."""
            # Extract the last user message
            messages = state.get("messages", [])
            last_user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
            
            if not last_user_message:
                return state
            
            try:
                # Query Pinecone with the user's message
                logger.info(f"Querying Pinecone for fiction content: {last_user_message[:50]}...")
                search_results = await pinecone_repo.search(last_user_message, limit=5)
                
                # Filter results to only include fiction
                fiction_results = [
                    result for result in search_results 
                    if result.get("data_type") == "FICTION" or 
                       result.get("source_type") == "fiction"
                ]
                
                # Ensure each result has a similarity_score field
                for result in fiction_results:
                    if "similarity_score" not in result:
                        # Use a default score if missing
                        result["similarity_score"] = 0.0
                
                # Update state with Pinecone results
                state["pinecone_results"] = fiction_results
                logger.info(f"Found {len(fiction_results)} fiction results in Pinecone")
                
                return state
            except Exception as e:
                logger.error(f"Error querying Pinecone: {str(e)}")
                # Continue without Pinecone results
                state["pinecone_results"] = []
                return state
        
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
            
            # Add Pinecone results to the system message if available
            pinecone_results = state.get("pinecone_results", [])
            if pinecone_results:
                # Format Pinecone results as context
                context = "I found the following fiction-related information that might be helpful:\n\n"
                for i, result in enumerate(pinecone_results, 1):
                    title = result.get("title", "Untitled")
                    content = result.get("content", "")
                    specified_text = result.get("specified_text", "")
                    reference = result.get("reference", "")
                    
                    context += f"{i}. {title}\n"
                    if specified_text:
                        context += f"   Quote: \"{specified_text}\"\n"
                    if content:
                        context += f"   Summary: {content}\n"
                    if reference:
                        context += f"   Reference: {reference}\n"
                    context += "\n"
                
                # Add context as a system message
                lc_messages.insert(0, SystemMessage(content=context))
            
            # Get response from LLM
            response = llm.invoke(lc_messages)
            
            # Add assistant's response to the messages
            state["messages"].append({
                "role": "assistant",
                "content": response.content
            })
            
            return state
        
        # Add nodes to the graph
        workflow.add_node("detect_fiction_topic", detect_fiction_topic)
        workflow.add_node("query_pinecone", query_pinecone)
        workflow.add_node("process_message", process_message)
        
        # Define edges
        workflow.add_edge("detect_fiction_topic", "query_pinecone")
        workflow.add_edge("detect_fiction_topic", "process_message")
        workflow.add_edge("query_pinecone", "process_message")
        workflow.add_edge("process_message", END)
        
        # Set the entry point
        workflow.set_entry_point("detect_fiction_topic")
        
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
        },
        "is_fiction_topic": False,
        "pinecone_results": []
    } 