import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """Configure logging for the application.
    
    Args:
        debug: Enable debug logging
        log_file: Path to log file. If None, logs to ~/.porkbun/porkbun.log
    """
    # Remove default handler
    logger.remove()
    
    # Determine log format based on debug mode
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{message}"
    ) if debug else (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "{message}"
    )
    
    # Add console handler
    level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=True
    )
    
    # Add file handler
    if log_file is None:
        log_file = str(Path.home() / ".porkbun" / "porkbun.log")
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add rotating file handler
    logger.add(
        log_file,
        format=log_format,
        level="DEBUG" if debug else "INFO",
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="1 month",  # Keep logs for 1 month
        compression="gz"  # Compress rotated logs
    )

def log_api_request(endpoint: str, data: Dict[str, Any], response: Dict[str, Any]) -> None:
    """Log API request and response for debugging.
    
    Args:
        endpoint: API endpoint
        data: Request data
        response: Response data
    """
    logger.debug(f"API Request - Endpoint: {endpoint}")
    logger.debug(f"Request Data: {data}")
    logger.debug(f"Response: {response}")

def log_command(command: str, args: Dict[str, Any]) -> None:
    """Log command execution.
    
    Args:
        command: Command name
        args: Command arguments
    """
    logger.info(f"Executing command: {command}")
    logger.debug(f"Command arguments: {args}")

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context.
    
    Args:
        error: Exception object
        context: Additional context
    """
    logger.error(f"Error: {str(error)}")
    if context:
        logger.debug(f"Error context: {context}")
    logger.debug("Stack trace:", exc_info=True) 