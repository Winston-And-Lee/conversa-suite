"""
Service to manage assistant-ui interactions with LangGraph.
"""
import logging
import uuid
import asyncio
import anyio
from anyio import get_cancelled_exc_class
from typing import Dict, List, Optional, Any, AsyncIterator
import json

from .assistant import create_assistant_ui_agent, create_initial_state, AssistantUIState

logger = logging.getLogger(__name__)

# In-memory store for assistant sessions (in production, use a database)
assistant_sessions: Dict[str, AssistantUIState] = {}
assistant_graph = create_assistant_ui_agent()

class AssistantUIService:
    """Service to manage assistant-ui interactions."""
    
    @staticmethod
    def create_thread(system_message: Optional[str] = None, assistant_id: Optional[str] = None) -> str:
        """Create a new assistant thread."""
        thread_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state = create_initial_state(assistant_id, system_message)
        assistant_sessions[thread_id] = initial_state
        
        logger.info(f"Created new assistant thread: {thread_id}")
        return thread_id
    
    @staticmethod
    async def send_message(thread_id: str, content: str) -> Dict[str, Any]:
        """Send a message to the assistant and get a response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Check if thread exists
            if thread_id not in assistant_sessions:
                logger.warning(f"Thread not found: {thread_id}")
                return {"error": "Thread not found"}
            
            # Get current state
            current_state = assistant_sessions[thread_id]
            
            # Add user message to the messages
            current_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Create tracing metadata
            metadata = {
                "thread_id": thread_id,
                "assistant_id": current_state.get("metadata", {}).get("assistant_id", "default"),
                "message_count": len(current_state.get("messages", [])),
                "source": "conversa_suite_api"
            }
            
            # Update metadata in state
            if "metadata" not in current_state:
                current_state["metadata"] = {}
            current_state["metadata"].update(metadata)
            
            # Run the agent graph
            result = await assistant_graph.ainvoke(current_state)
            
            # Update session state
            assistant_sessions[thread_id] = result
            
            # Return formatted response
            return {
                "thread_id": thread_id,
                "messages": result["messages"]
            }
            
        except (CancelledExc, asyncio.CancelledError) as e:
            logger.info(f"Operation cancelled for thread {thread_id}: {str(e)}")
            # Return a partial result if possible
            return {
                "thread_id": thread_id,
                "messages": current_state.get("messages", [])
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    @staticmethod
    async def stream_message(thread_id: str, content: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream a message to the assistant and get streaming response."""
        try:
            # Get the cancelled exception class inside the function scope
            CancelledExc = get_cancelled_exc_class()
            
            # Check if thread exists
            if thread_id not in assistant_sessions:
                logger.warning(f"Thread not found: {thread_id}")
                yield {"error": "Thread not found"}
                return
            
            # Get current state
            current_state = assistant_sessions[thread_id]
            
            # Add user message to the messages
            current_state["messages"].append({
                "role": "user",
                "content": content
            })
            
            # Create a placeholder for the assistant's response
            current_state["messages"].append({
                "role": "assistant",
                "content": ""
            })
            
            # Create tracing metadata
            metadata = {
                "thread_id": thread_id,
                "assistant_id": current_state.get("metadata", {}).get("assistant_id", "default"),
                "message_count": len(current_state.get("messages", [])),
                "source": "conversa_suite_api"
            }
            
            # Update metadata in state
            if "metadata" not in current_state:
                current_state["metadata"] = {}
            current_state["metadata"].update(metadata)
            
            # Convert messages to LangChain format for the LLM
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            lc_messages = []
            for msg in current_state["messages"][:-1]:  # Exclude the empty assistant message
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
            
            # Create the language model
            from ..model import create_llm
            llm = create_llm(
                run_name=f"Thread {thread_id[:8]} - Streaming",
                metadata=metadata,
                streaming=True
            )
            
            # Stream the response
            assistant_response = ""
            try:
                async for chunk in llm.astream(lc_messages):
                    # Append the new content to the assistant's response
                    assistant_response += chunk.content
                    
                    # Update the last message with the accumulated response
                    current_state["messages"][-1]["content"] = assistant_response
                    
                    # Yield the updated messages as a dictionary
                    yield {
                        "thread_id": thread_id,
                        "messages": current_state["messages"]
                    }
                
                # Update session state with the final response
                assistant_sessions[thread_id] = current_state
                logger.info(f"Successfully completed streaming for thread {thread_id}")
                
            except (CancelledExc, asyncio.CancelledError) as e:
                # Client disconnected - still save what we generated so far
                logger.info(f"Streaming cancelled for thread {thread_id}, saving partial response")
                if assistant_response:
                    current_state["messages"][-1]["content"] = assistant_response
                    assistant_sessions[thread_id] = current_state
                raise  # Re-raise to be caught by the outer handler
            
        except (CancelledExc, asyncio.CancelledError) as e:
            # This will be caught by the routes and handled there
            logger.info(f"Stream cancelled for thread {thread_id}")
            raise
        except Exception as e:
            logger.error(f"Error processing streaming message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            yield {"error": str(e)}
    
    @staticmethod
    def get_thread_messages(thread_id: str) -> List[Dict[str, str]]:
        """Get the message history for a thread."""
        if thread_id not in assistant_sessions:
            logger.warning(f"Thread not found: {thread_id}")
            return []
        
        # Get messages from the state
        state = assistant_sessions[thread_id]
        return state["messages"]
    
    @staticmethod
    def delete_thread(thread_id: str) -> bool:
        """Delete an assistant thread."""
        if thread_id in assistant_sessions:
            del assistant_sessions[thread_id]
            logger.info(f"Deleted assistant thread: {thread_id}")
            return True
        
        logger.warning(f"Thread not found for deletion: {thread_id}")
        return False


# Create singleton instance
assistant_service = AssistantUIService() 