"""Translate infrastructure errors into safe client-facing responses."""

import logging


def user_friendly_error(error: Exception, operation: str) -> str:
    """Return a stable response without exposing providers, secrets, or traces."""
    message = str(error).lower()
    if any(token in message for token in ("credit", "quota", "402", "insufficient")):
        return "The language model is temporarily unavailable due to API quota. Please retry in a few minutes."
    if any(token in message for token in ("max tokens", "length", "context", "finishreason")):
        return "The response exceeded the model's generation limit. Please ask a more focused question or try again."
    if any(token in message for token in ("timeout", "timed out", "deadline")):
        return f"{operation} timed out. Please try again."
    if any(token in message for token in ("rate limit", "429", "too many requests")):
        return "The service is busy right now. Please retry in a moment."
    if any(token in message for token in ("api key", "authentication", "unauthorized", "forbidden", "missing")):
        return f"{operation} is not configured correctly. Please contact an administrator."
    return f"{operation} is temporarily unavailable. Please try again."


def log_failure(logger: logging.Logger, operation: str, error: Exception) -> None:
    """Keep diagnostic detail in logs while withholding it from clients."""
    logger.exception("operation_failed operation=%s error_type=%s", operation, type(error).__name__)
