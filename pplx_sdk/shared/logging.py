"""Structured logging utilities."""

import logging
import sys


def get_logger(
    name: str,
    level: int = logging.INFO,
    format_string: str | None = None,
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add handler if logger doesn't have any handlers yet
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Set format
        if not format_string:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


def configure_root_logger(level: int = logging.INFO) -> None:
    """Configure the root logger for the SDK.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# Default logger for the SDK
sdk_logger = get_logger("pplx_sdk")
