"""
Logger Configuration Module

This module sets up logging for the entire application with:
- File and console logging
- Proper log formatting
- Log rotation
- Different log levels
"""

import os
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days"
) -> logger:
    """
    Set up application logging with loguru
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        rotation: Log rotation size
        retention: How long to keep old logs
        
    Returns:
        Configured logger instance
    """
    
    # Remove default logger
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # File logging (if specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
    
    return logger


def get_logger(name: str = None) -> logger:
    """
    Get logger instance for a specific module
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize default logger
default_log_file = os.path.join("logs", "linkedin_automation.log")
setup_logger(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=default_log_file
)
