# common/logger.py
import logging
import sys
from config import LOG_LEVEL

def setup_logger():
    """Sets up a basic console logger."""
    logger = logging.getLogger("PacallerGenerator")
    if logger.hasHandlers():
        return logger

    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger