import logging
import os
from typing import Optional

class LoggingConfig:
    """Configuration class for logging settings"""
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_file: str = "logs/ktmb_scraper.log",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True
    ):
        self.log_level = log_level.upper()
        self.log_file = log_file
        self.log_format = log_format
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_output = console_output
        self.file_output = file_output

def setup_logging(config: Optional[LoggingConfig] = None) -> logging.Logger:
    """
    Setup logging configuration with the provided settings
    
    Args:
        config: LoggingConfig object with logging settings. If None, uses defaults.
    
    Returns:
        Configured logger instance
    """
    if config is None:
        config = LoggingConfig()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create handlers list
    handlers = []
    
    # File handler with rotation
    if config.file_output:
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                config.log_file,
                maxBytes=config.max_file_size,
                backupCount=config.backup_count
            )
            file_handler.setFormatter(logging.Formatter(config.log_format))
            handlers.append(file_handler)
        except ImportError:
            # Fallback to basic FileHandler if RotatingFileHandler not available
            file_handler = logging.FileHandler(config.log_file)
            file_handler.setFormatter(logging.Formatter(config.log_format))
            handlers.append(file_handler)
    
    # Console handler
    if config.console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(config.log_format))
        handlers.append(console_handler)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    return logging.getLogger(__name__)

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name. If None, returns the root logger.
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

# Predefined logging configurations
def get_debug_config() -> LoggingConfig:
    """Get debug logging configuration"""
    return LoggingConfig(
        log_level="DEBUG",
        log_file="logs/ktmb_scraper_debug.log",
        console_output=True,
        file_output=True
    )

def get_production_config() -> LoggingConfig:
    """Get production logging configuration"""
    return LoggingConfig(
        log_level="INFO",
        log_file="logs/ktmb_scraper.log",
        console_output=False,
        file_output=True
    )

def get_quiet_config() -> LoggingConfig:
    """Get quiet logging configuration (errors only)"""
    return LoggingConfig(
        log_level="ERROR",
        log_file="logs/ktmb_scraper_error.log",
        console_output=True,
        file_output=True
    ) 