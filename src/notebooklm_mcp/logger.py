import logging
import os
from .config import config


def setup_logger():
    logger = logging.getLogger("notebooklm_mcp")

    # If logger already has handlers, return it to avoid duplication
    if logger.handlers:
        return logger

    # Prevent logs from propagating to the root logger (FastMCP handles its own)
    logger.propagate = False

    # Set log level
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    log_file = config.LOG_FILE
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


logger = setup_logger()
