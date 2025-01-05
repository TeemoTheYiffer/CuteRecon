import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name (str): Logger name (e.g., 'openai', 'claude', 'discord')
        log_file (str, optional): Path to log file
        level (int): Logging level
    """
    # Create logger with name
    logger = logging.getLogger(name)
    logger.handlers = []  # Clear existing handlers
    logger.propagate = False  # Prevent propagation to root logger
    logger.setLevel(level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] {%(name)s} %(levelname)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)
        
    # File handler if specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # Keep 5 backup files
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger
