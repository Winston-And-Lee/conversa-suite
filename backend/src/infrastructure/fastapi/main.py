# This file is kept for backward compatibility
# All functionality has been moved to server.py

from src.infrastructure.fastapi.server import create_app, lifespan

# Create an app instance for backward compatibility
app = create_app()

# Re-export for backward compatibility
__all__ = ['create_app', 'lifespan', 'app'] 