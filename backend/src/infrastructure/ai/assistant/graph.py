"""
LangGraph implementation for the assistant service.
"""
import logging
from typing import Dict, List, Any, TypedDict, Annotated, Literal, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

from src.infrastructure.ai.model import create_llm
from src.interface.repository.database.db_repository import pinecone_repository

logger = logging.getLogger(__name__)

# Define the state schema
class AssistantState(TypedDict):
    """State for the assistant graph."""
    thread_id: str
    messages: List[Dict[str, Any]]
    system_message: Optional[str]
    is_fiction_topic: bool
    fiction_sources: List[Dict[str, Any]]
    current_response: str
    metadata: Dict[str, Any]

# Fiction detection node
async def detect_fiction_topic(state: AssistantState) -> AssistantState:
    """Detect if the user's message is about fiction."""
    try:
        # Get the last user message
        last_user_message = ""
        for msg in reversed(state["messages"]):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if not last_user_message:
            logger.warning("No user message found for fiction detection")
            state["is_fiction_topic"] = False
            return state
        
        # Use a separate LLM call to classify the topic
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
        
        state["is_fiction_topic"] = is_fiction
        logger.info(f"Fiction detection result: {is_fiction} for message: {last_user_message[:50]}...")
        
        return state
    except Exception as e:
        logger.error(f"Error in fiction detection: {str(e)}")
        state["is_fiction_topic"] = False
        return state

# Fiction search node
async def search_fiction_sources(state: AssistantState) -> AssistantState:
    """Search for fiction sources if the topic is about fiction."""
    try:
        if not state["is_fiction_topic"]:
            state["fiction_sources"] = []
            return state
        
        # Get the last user message
        last_user_message = ""
        for msg in reversed(state["messages"]):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        if not last_user_message:
            logger.warning("No user message found for fiction search")
            state["fiction_sources"] = []
            return state
        
        # Import and initialize Pinecone repository
        pinecone_repo = pinecone_repository()
        
        # Query Pinecone
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
        
        logger.info(f"Found {len(fiction_results)} fiction results in Pinecone")
        state["fiction_sources"] = fiction_results
        
        return state
    except Exception as e:
        logger.error(f"Error in fiction search: {str(e)}")
        state["fiction_sources"] = []
        return state

# Prepare context node
async def prepare_context(state: AssistantState) -> AssistantState:
    """Prepare the context for the LLM based on the state."""
    try:
        # Convert messages to LangChain format for the LLM
        lc_messages = []
        
        # Add system message if available
        if state["system_message"]:
            lc_messages.append(SystemMessage(content=state["system_message"]))
        
        # Add fiction context if available
        if state["is_fiction_topic"] and state["fiction_sources"]:
            context = "I found the following fiction-related information that might be helpful:\n\n"
            for i, result in enumerate(state["fiction_sources"], 1):
                title = result.get("title", "Untitled")
                content_text = result.get("content", "")
                specified_text = result.get("specified_text", "")
                reference = result.get("reference", "")
                
                context += f"{i}. {title}\n"
                if specified_text:
                    context += f"   Quote: \"{specified_text}\"\n"
                if content_text:
                    context += f"   Summary: {content_text}\n"
                if reference:
                    context += f"   Reference: {reference}\n"
                context += "\n"
            
            # Add context as a system message
            lc_messages.append(SystemMessage(content=context))
        
        # Add conversation messages
        for msg in state["messages"]:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system" and not state["system_message"]:
                lc_messages.append(SystemMessage(content=msg["content"]))
        
        # Create the language model
        llm = create_llm(
            run_name=f"Thread {state['thread_id'][:8]} - Processing",
            metadata=state["metadata"],
        )
        
        # Get response from LLM
        response = llm.invoke(lc_messages)
        state["current_response"] = response.content
        
        return state
    except Exception as e:
        logger.error(f"Error preparing context: {str(e)}")
        state["current_response"] = "I apologize, but I'm experiencing technical difficulties. Please try again later."
        return state

# Create the graph
def create_assistant_graph():
    """Create the assistant graph."""
    # Define the graph
    graph = StateGraph(AssistantState)
    
    # Add nodes
    graph.add_node("detect_fiction", detect_fiction_topic)
    graph.add_node("search_fiction", search_fiction_sources)
    graph.add_node("prepare_context", prepare_context)
    
    # Define the branch function
    def branch_fiction(state: AssistantState) -> str:
        """Branch based on fiction detection."""
        return "search_fiction" if state["is_fiction_topic"] else "prepare_context"
    
    # Add the edges with conditional branching
    graph.add_conditional_edges(
        "detect_fiction",
        branch_fiction,
        {
            "search_fiction": "search_fiction",
            "prepare_context": "prepare_context"
        }
    )
    graph.add_edge("search_fiction", "prepare_context")
    graph.add_edge("prepare_context", END)
    
    # Set the entry point
    graph.set_entry_point("detect_fiction")
    
    # Compile the graph
    return graph.compile()

# Create a streaming version of the graph
def create_streaming_assistant_graph():
    """Create a streaming version of the assistant graph."""
    # Define the graph
    graph = StateGraph(AssistantState)
    
    # Add nodes
    graph.add_node("detect_fiction", detect_fiction_topic)
    graph.add_node("search_fiction", search_fiction_sources)
    
    # For streaming, we'll use a different approach for the LLM
    async def streaming_llm_node(state: AssistantState):
        """Node that streams responses from the LLM."""
        try:
            # Convert messages to LangChain format for the LLM
            lc_messages = []
            
            # Add system message if available
            if state["system_message"]:
                lc_messages.append(SystemMessage(content=state["system_message"]))
            
            # Add fiction context if available
            if state["is_fiction_topic"] and state["fiction_sources"]:
                context = "I found the following fiction-related information that might be helpful:\n\n"
                for i, result in enumerate(state["fiction_sources"], 1):
                    title = result.get("title", "Untitled")
                    content_text = result.get("content", "")
                    specified_text = result.get("specified_text", "")
                    reference = result.get("reference", "")
                    
                    context += f"{i}. {title}\n"
                    if specified_text:
                        context += f"   Quote: \"{specified_text}\"\n"
                    if content_text:
                        context += f"   Summary: {content_text}\n"
                    if reference:
                        context += f"   Reference: {reference}\n"
                    context += "\n"
                
                # Add context as a system message
                lc_messages.append(SystemMessage(content=context))
            
            # Add conversation messages
            last_user_message = ""
            for msg in state["messages"]:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                    last_user_message = msg["content"]
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system" and not state["system_message"]:
                    lc_messages.append(SystemMessage(content=msg["content"]))
            
            # Ensure we have at least one message
            if not lc_messages:
                logger.warning(f"No messages found for thread {state['thread_id']}, adding default messages")
                lc_messages = [
                    SystemMessage(content="You are a helpful assistant."),
                    HumanMessage(content=last_user_message or "Hello")
                ]
            elif all(isinstance(msg, SystemMessage) for msg in lc_messages):
                # If we only have system messages, add a default user message
                logger.warning(f"Only system messages found for thread {state['thread_id']}, adding default user message")
                lc_messages.append(HumanMessage(content=last_user_message or "Hello"))
            
            # Create the language model with streaming enabled
            llm = create_llm(
                run_name=f"Thread {state['thread_id'][:8]} - Streaming",
                metadata=state["metadata"],
                streaming=True
            )
            
            # Make sure the LLM is not None
            if llm is None:
                logger.error(f"Failed to create LLM for thread {state['thread_id']}, using fallback")
                # Create a fallback LLM
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                    streaming=True
                )
            
            # This node will be used differently in the service.py file
            # to handle streaming, so we just return the state here
            state["llm"] = llm
            state["lc_messages"] = lc_messages
            
            logger.info(f"Streaming LLM node prepared for thread {state['thread_id']} with {len(lc_messages)} messages")
            return state
        except Exception as e:
            logger.error(f"Error in streaming LLM node: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            state["current_response"] = "I apologize, but I'm experiencing technical difficulties. Please try again later."
            return state
    
    graph.add_node("streaming_llm", streaming_llm_node)
    
    # Define the branch function
    def branch_fiction(state: AssistantState) -> str:
        """Branch based on fiction detection."""
        return "search_fiction" if state["is_fiction_topic"] else "streaming_llm"
    
    # Add the edges with conditional branching
    graph.add_conditional_edges(
        "detect_fiction",
        branch_fiction,
        {
            "search_fiction": "search_fiction",
            "streaming_llm": "streaming_llm"
        }
    )
    graph.add_edge("search_fiction", "streaming_llm")
    graph.add_edge("streaming_llm", END)
    
    # Set the entry point
    graph.set_entry_point("detect_fiction")
    
    # Compile the graph
    app = graph.compile()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    return app

# Helper function to initialize the state
def initialize_state(thread_id: str, messages: List[Dict[str, Any]], system_message: Optional[str] = None) -> AssistantState:
    """Initialize the state for the assistant graph."""
    return {
        "thread_id": thread_id,
        "messages": messages,
        "system_message": system_message,
        "is_fiction_topic": False,
        "fiction_sources": [],
        "current_response": "",
        "metadata": {
            "thread_id": thread_id,
            "message_count": len(messages),
            "source": "conversa_suite_api"
        }
    } 