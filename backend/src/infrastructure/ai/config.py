"""
Configuration for AI models and services.
"""
from src.config.settings import get_settings

# Load settings from environment
settings = get_settings()

# OpenAI API settings
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = settings.OPENAI_MODEL

# LangGraph settings
ASSISTANT_ID = settings.LANGGRAPH_ASSISTANT_ID

# Default system message for chatbot
DEFAULT_SYSTEM_MESSAGE = """You are a helpful AI assistant that is polite, friendly, and informative.
You provide concise and accurate responses based on the information you have.
If you don't know something, simply say so rather than making up information.
""" 