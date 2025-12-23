"""Logging system for Rejoice."""

import logging
import logging.handlers
from pathlib import Path

from rich.logging import RichHandler

from rejoice.core.config import get_config_dir


def get_log_dir() -> Path:
    """Get the logging directory."""
    config_dir = get_config_dir()
    log_dir = config_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration.

    Args:
        debug: If True, enable DEBUG level logging. Otherwise, use INFO.
    """
    log_dir = get_log_dir()
    log_file = log_dir / "rejoice.log"

    # Ensure log directory exists (in case get_log_dir was patched in tests)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Determine log level
    level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler with Rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        markup=True,
    )
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
