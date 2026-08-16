"""Application logging configuration used by API, agents, and tools."""

import logging
import sys

from app.config import LOG_LEVEL


def configure_logging() -> None:
    """Configure structured, single-line logs once for the application."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return
    logging.basicConfig(
        level=LOG_LEVEL,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
