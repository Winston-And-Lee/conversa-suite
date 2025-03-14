#!/usr/bin/env python
"""
Test script for the fiction detection and Pinecone querying in the assistant.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.src.infrastructure.ai.langgraph.assistant_service import AssistantUIService
from backend.src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def test_fiction_detection():
    """Test the fiction detection and Pinecone querying in the assistant."""
    try:
        # Create a new assistant thread
        system_message = "You are a helpful assistant that can answer questions about fiction and other topics."
        thread_id = AssistantUIService.create_thread(system_message=system_message)
        logger.info(f"Created new thread: {thread_id}")
        
        # Test with a fiction-related query
        fiction_query = "Tell me about Snow White and the Seven Dwarfs."
        logger.info(f"Sending fiction query: {fiction_query}")
        
        try:
            fiction_response = await AssistantUIService.send_message(thread_id, fiction_query)
            
            # Check for errors in the response
            if "error" in fiction_response:
                logger.error(f"Error in fiction response: {fiction_response['error']}")
            else:
                # Check if fiction was detected
                if fiction_response.get("is_fiction_topic"):
                    logger.info("✅ Fiction topic correctly detected")
                    
                    # Check if Pinecone results were returned
                    if fiction_response.get("fiction_sources"):
                        logger.info(f"✅ Found {len(fiction_response['fiction_sources'])} fiction sources in Pinecone")
                        for i, source in enumerate(fiction_response["fiction_sources"], 1):
                            logger.info(f"  {i}. {source['title']} (Score: {source.get('similarity_score', 0.0):.4f})")
                    else:
                        logger.info("❌ No fiction sources found in Pinecone")
                else:
                    logger.info("❌ Fiction topic not detected")
                
                # Print the assistant's response
                logger.info("\nAssistant's response:")
                for msg in fiction_response["messages"]:
                    if msg["role"] == "assistant":
                        logger.info(f"{msg['content']}")
        except Exception as e:
            logger.error(f"Error processing fiction query: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Test with a non-fiction query
        non_fiction_query = "What is the capital of France?"
        logger.info(f"\nSending non-fiction query: {non_fiction_query}")
        
        try:
            non_fiction_response = await AssistantUIService.send_message(thread_id, non_fiction_query)
            
            # Check for errors in the response
            if "error" in non_fiction_response:
                logger.error(f"Error in non-fiction response: {non_fiction_response['error']}")
            else:
                # Check if fiction was not detected
                if not non_fiction_response.get("is_fiction_topic", True):
                    logger.info("✅ Non-fiction topic correctly identified")
                else:
                    logger.info("❌ Non-fiction topic incorrectly classified as fiction")
                
                # Print the assistant's response
                logger.info("\nAssistant's response:")
                for msg in non_fiction_response["messages"]:
                    if msg["role"] == "assistant":
                        logger.info(f"{msg['content']}")
        except Exception as e:
            logger.error(f"Error processing non-fiction query: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Test streaming with fiction query
        streaming_query = "Tell me about Beauty and the Beast."
        logger.info(f"\nTesting streaming with fiction query: {streaming_query}")
        
        try:
            # Collect all streaming responses
            streaming_responses = []
            async for response in AssistantUIService.stream_message(thread_id, streaming_query):
                if "error" in response:
                    logger.error(f"Streaming error: {response['error']}")
                    break
                
                # Store the response
                streaming_responses.append(response)
                
                # Log fiction detection info from the first response
                if len(streaming_responses) == 1:
                    if response.get("is_fiction_topic"):
                        logger.info("✅ Fiction topic correctly detected in streaming")
                        
                        # Check if Pinecone results were returned
                        if response.get("fiction_sources"):
                            logger.info(f"✅ Found {len(response['fiction_sources'])} fiction sources in streaming")
                            for i, source in enumerate(response['fiction_sources'], 1):
                                logger.info(f"  {i}. {source['title']} (Score: {source.get('similarity_score', 0.0):.4f})")
                        else:
                            logger.info("❌ No fiction sources found in streaming")
                    else:
                        logger.info("❌ Fiction topic not detected in streaming")
            
            # Print the final streaming response
            if streaming_responses:
                final_response = streaming_responses[-1]
                logger.info("\nFinal streaming response:")
                for msg in final_response["messages"]:
                    if msg["role"] == "assistant":
                        logger.info(f"{msg['content']}")
            else:
                logger.warning("No streaming responses received")
        except Exception as e:
            logger.error(f"Error processing streaming query: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Clean up
        try:
            deleted = AssistantUIService.delete_thread(thread_id)
            logger.info(f"Thread deleted: {deleted}")
        except Exception as e:
            logger.error(f"Error deleting thread: {str(e)}")
        
        logger.info("Fiction detection test completed")
        
    except Exception as e:
        logger.error(f"Error testing fiction detection: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_fiction_detection()) 