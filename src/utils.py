import logging
import sys
from pathlib import Path
from config.config import LOGS_DIR, LOG_LEVEL

def setup_logging() -> None:
    """Set up logging configuration."""
    # Convert string to logging level
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    log_file = LOGS_DIR / "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.info("Logging configured successfully.")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: The name for the logger (usually __name__).

    Returns:
        A logger instance.
    """
    return logging.getLogger(name)
