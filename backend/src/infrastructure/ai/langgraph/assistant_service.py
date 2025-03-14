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
            
            # Return formatted response with fiction detection info
            response = {
                "thread_id": thread_id,
                "messages": result["messages"]
            }
            
            # Add fiction detection info if available
            if "is_fiction_topic" in result:
                response["is_fiction_topic"] = result["is_fiction_topic"]
                
                # Include pinecone results summary if it's a fiction topic
                if result["is_fiction_topic"] and result.get("pinecone_results"):
                    response["fiction_sources"] = [
                        {
                            "title": item.get("title", "Untitled"),
                            "reference": item.get("reference", ""),
                            "similarity_score": item.get("similarity_score", 0.0)
                        }
                        for item in result.get("pinecone_results", [])
                    ]
            
            return response
            
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
            
            # Initialize fiction detection fields
            current_state["is_fiction_topic"] = False
            current_state["pinecone_results"] = []
            
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
            
            # First, check if the message is about fiction
            try:
                # Use a separate LLM call to classify the topic
                classification_prompt = [
                    SystemMessage(content="You are a topic classifier. Determine if the user's message is about fiction (novels, stories, fairy tales, etc.). Respond with only 'YES' if it's about fiction or 'NO' if it's not."),
                    HumanMessage(content=content)
                ]
                
                classification_llm = create_llm(
                    run_name="Fiction Topic Classification - Streaming",
                    metadata={"task": "fiction_classification"}
                )
                
                classification_result = classification_llm.invoke(classification_prompt)
                is_fiction = "YES" in classification_result.content.upper()
                
                # Update state with classification result
                current_state["is_fiction_topic"] = is_fiction
                
                # If it's about fiction, query Pinecone
                if is_fiction:
                    logger.info(f"Detected fiction topic in streaming message: {content[:50]}...")
                    
                    # Import and initialize Pinecone repository
                    from src.interface.repository.database.db_repository import pinecone_repository
                    pinecone_repo = pinecone_repository()
                    
                    # Query Pinecone
                    search_results = await pinecone_repo.search(content, limit=5)
                    
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
                    current_state["pinecone_results"] = fiction_results
                    logger.info(f"Found {len(fiction_results)} fiction results in Pinecone for streaming")
                    
                    # Add context from Pinecone results
                    if fiction_results:
                        context = "I found the following fiction-related information that might be helpful:\n\n"
                        for i, result in enumerate(fiction_results, 1):
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
                        lc_messages.insert(0, SystemMessage(content=context))
            except Exception as e:
                logger.error(f"Error in fiction detection during streaming: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Continue without fiction detection
            
            # Stream the response
            assistant_response = ""
            try:
                async for chunk in llm.astream(lc_messages):
                    # Append the new content to the assistant's response
                    assistant_response += chunk.content
                    
                    # Update the last message with the accumulated response
                    current_state["messages"][-1]["content"] = assistant_response
                    
                    # Prepare response with fiction detection info
                    response = {
                        "thread_id": thread_id,
                        "messages": current_state["messages"]
                    }
                    
                    # Add fiction detection info if available
                    if current_state.get("is_fiction_topic"):
                        response["is_fiction_topic"] = current_state["is_fiction_topic"]
                        
                        # Include pinecone results summary if it's a fiction topic
                        if current_state["is_fiction_topic"] and current_state.get("pinecone_results"):
                            response["fiction_sources"] = [
                                {
                                    "title": item.get("title", "Untitled"),
                                    "reference": item.get("reference", ""),
                                    "similarity_score": item.get("similarity_score", 0.0)
                                }
                                for item in current_state.get("pinecone_results", [])
                            ]
                    
                    # Yield the updated response
                    yield response
                
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