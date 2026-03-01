"""
Logging configuration for the application.
Provides centralized logging setup.
"""
import logging
import sys
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # Console handler
        logging.StreamHandler(sys.stdout),
        # File handler
        logging.FileHandler(LOGS_DIR / "app.log"),
    ]
)

# Create logger
logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Module-level logger for core utilities
audit_logger = logging.getLogger("audit")
db_logger = logging.getLogger("database")
security_logger = logging.getLogger("security")
