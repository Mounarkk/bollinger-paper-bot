# File: utils/logger.py

import logging
from datetime import datetime

def get_logger(name: str, log_file: str = "application.log"):
    """
    Set up and return a logger instance.

    Parameters:
        name (str): Name of the logger.
        log_file (str): Log file path.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Formatter for log messages
    formatter = logging.Formatter(
        fmt="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
