"""Tests for core module (exceptions, protocols, types)."""

import pytest

from pplx_sdk.core.exceptions import (
    AuthenticationError,
    PerplexitySDKError,
    RateLimitError,
    StreamingError,
    TransportError,
    ValidationError,
)
from pplx_sdk.core.protocols import StreamParser, Transport


def test_perplexity_sdk_error() -> None:
    """Test base SDK error."""
    error = PerplexitySDKError("test error", details={"key": "value"})
    assert str(error) == "test error"
    assert error.message == "test error"
    assert error.details == {"key": "value"}


def test_perplexity_sdk_error_default_details() -> None:
    """Test base SDK error with default details."""
    error = PerplexitySDKError("test error")
    assert error.details == {}


def test_transport_error() -> None:
    """Test transport error with status code and body."""
    error = TransportError("HTTP 500", status_code=500, response_body="Internal Error")
    assert str(error) == "HTTP 500"
    assert error.status_code == 500
    assert error.response_body == "Internal Error"
    assert isinstance(error, PerplexitySDKError)


def test_authentication_error() -> None:
    """Test authentication error inherits from transport error."""
    error = AuthenticationError("Invalid token", status_code=401)
    assert isinstance(error, TransportError)
    assert isinstance(error, PerplexitySDKError)
    assert error.status_code == 401


def test_rate_limit_error() -> None:
    """Test rate limit error with retry_after."""
    error = RateLimitError("Too many requests", retry_after=60)
    assert isinstance(error, TransportError)
    assert error.status_code == 429
    assert error.retry_after == 60


def test_streaming_error() -> None:
    """Test streaming error."""
    error = StreamingError("Connection lost")
    assert isinstance(error, PerplexitySDKError)
    assert str(error) == "Connection lost"


def test_validation_error() -> None:
    """Test validation error."""
    error = ValidationError("Invalid request")
    assert isinstance(error, PerplexitySDKError)
    assert str(error) == "Invalid request"


def test_exception_hierarchy() -> None:
    """Test exception inheritance chain."""
    # All SDK errors should be caught by PerplexitySDKError
    with pytest.raises(PerplexitySDKError):
        raise TransportError("transport")

    with pytest.raises(PerplexitySDKError):
        raise AuthenticationError("auth")

    with pytest.raises(PerplexitySDKError):
        raise RateLimitError("rate limit")

    with pytest.raises(PerplexitySDKError):
        raise StreamingError("streaming")

    with pytest.raises(PerplexitySDKError):
        raise ValidationError("validation")

    # Transport errors should be caught by TransportError
    with pytest.raises(TransportError):
        raise AuthenticationError("auth")

    with pytest.raises(TransportError):
        raise RateLimitError("rate limit")


def test_transport_protocol() -> None:
    """Test Transport protocol is runtime checkable."""
    assert hasattr(Transport, "request")
    assert hasattr(Transport, "stream")


def test_stream_parser_protocol() -> None:
    """Test StreamParser protocol is runtime checkable."""
    assert hasattr(StreamParser, "parse_event")
