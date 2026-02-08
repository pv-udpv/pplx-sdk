"""SDK-wide exception hierarchy."""

from __future__ import annotations

from typing import Any


class PerplexitySDKError(Exception):
    """Base exception for all SDK errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TransportError(PerplexitySDKError):
    """Transport-level errors (network, timeout, HTTP errors)."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(TransportError):
    """Authentication failures (401, invalid token)."""

    pass


class RateLimitError(TransportError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class StreamingError(PerplexitySDKError):
    """SSE streaming errors (disconnect, parse errors)."""

    pass


class ValidationError(PerplexitySDKError):
    """Request/response validation errors."""

    pass
