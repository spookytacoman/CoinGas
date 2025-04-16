import uvicorn
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("coinGas.log")
    ]
)
logger = logging.getLogger("server")

# Load environment variables
load_dotenv()

def start_server():
    """
    Start the CoinGas API server.
    
    This function configures and starts the FastAPI server using uvicorn.
    It loads environment variables and sets up the server configuration.
    """
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Get host from environment variable or use default
    host = os.getenv("HOST", "0.0.0.0")
    
    # Get reload flag from environment variable or use default
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    logger.info(f"Starting CoinGas API server on {host}:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Change to the parent directory (project root)
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 