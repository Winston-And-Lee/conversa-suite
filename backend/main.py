import uvicorn
import logging
import sys
from src.infrastructure.fastapi.server import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to DEBUG level
for logger_name in ["src.infrastructure.database", "src.interface.repository", "src.usecase"]:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
app = create_app()

if __name__ == "__main__":
    from src.config.settings import get_settings
    settings = get_settings()
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 