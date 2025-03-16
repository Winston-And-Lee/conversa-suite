"""
Service to manage chatbot interactions with LangGraph.
"""
import logging
import uuid
from typing import Dict, List, Optional, Any

from .agent import create_chat_agent, process_input, create_initial_state, ChatState

logger = logging.getLogger(__name__)

# In-memory store for chat sessions (in production, use a database)
chat_sessions: Dict[str, ChatState] = {}
graph = create_chat_agent()

class ChatbotService:
    """Service to manage chatbot interactions."""
    
    @staticmethod
    def create_session(assistant_id: Optional[str] = None) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state = create_initial_state(assistant_id)
        chat_sessions[session_id] = initial_state
        
        logger.info(f"Created new chat session: {session_id}")
        return session_id
    
    @staticmethod
    async def send_message(session_id: str, message: str) -> Dict[str, Any]:
        """Send a message to the chatbot and get a response."""
        # Check if session exists
        if session_id not in chat_sessions:
            logger.warning(f"Session not found: {session_id}")
            return {"error": "Session not found"}
        
        try:
            # Get current state
            current_state = chat_sessions[session_id]
            
            # Process user input
            updated_state = process_input(current_state, message)
            
            # Create tracing metadata
            metadata = {
                "session_id": session_id,
                "assistant_id": current_state.get("assistant_id", "default"),
                "message_count": len(current_state.get("messages", [])),
                "source": "conversa_suite_api"
            }
            
            # Add run name with session context for LangSmith
            run_name = f"Session {session_id[:8]} - Message {len(current_state.get('messages', []))}"
            
            # Add metadata to state for tracing
            updated_state["_metadata"] = metadata
            updated_state["_run_name"] = run_name
            
            # Log tracing information
            logger.info(f"Processing message with run_name: {run_name}")
            
            # Run the agent graph
            result = await graph.ainvoke(updated_state)
            
            # Update session state
            chat_sessions[session_id] = result
            
            # Extract the last assistant message from the state
            messages = result["messages"]
            
            # Handle the case when the last message is an AIMessage object
            if len(messages) > 0:
                last_message = messages[-1]
                if isinstance(last_message, dict) and last_message.get("role") == "assistant":
                    response = last_message["content"]
                else:
                    # If it's not a dictionary but an AIMessage object
                    from langchain_core.messages import AIMessage
                    if isinstance(last_message, AIMessage):
                        response = last_message.content
                    else:
                        # Add a new assistant message if none is present
                        response = "No response generated."
                        messages.append({
                            "role": "assistant",
                            "content": response
                        })
            else:
                response = "No response generated."
                messages.append({
                    "role": "assistant",
                    "content": response
                })
            
            # Convert any LangChain message objects to dictionaries for the response
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    formatted_messages.append(msg)
                elif hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # Handle LangChain message objects
                    role = "assistant" if msg.type == "ai" else "user" if msg.type == "human" else "system"
                    formatted_messages.append({
                        "role": role,
                        "content": msg.content
                    })
            
            return {
                "session_id": session_id,
                "response": response,
                "messages": formatted_messages
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    @staticmethod
    def get_session_history(session_id: str) -> List[Dict[str, str]]:
        """Get the message history for a session."""
        if session_id not in chat_sessions:
            logger.warning(f"Session not found: {session_id}")
            return []
        
        # Get messages from the state
        state = chat_sessions[session_id]
        messages = state["messages"]
        
        # Ensure all messages are in dictionary format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            elif hasattr(msg, 'type') and hasattr(msg, 'content'):
                # Handle LangChain message objects
                role = "assistant" if msg.type == "ai" else "user" if msg.type == "human" else "system"
                formatted_messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        return formatted_messages
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in chat_sessions:
            del chat_sessions[session_id]
            logger.info(f"Deleted chat session: {session_id}")
            return True
        
        logger.warning(f"Session not found for deletion: {session_id}")
        return False


# Create singleton instance
chatbot_service = ChatbotService() 