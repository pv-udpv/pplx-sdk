"""Core abstractions and types."""

from pplx_sdk.core.exceptions import (
    AuthenticationError,
    PerplexitySDKError,
    RateLimitError,
    StreamingError,
    TransportError,
    ValidationError,
)
from pplx_sdk.core.protocols import StreamParser, Transport
from pplx_sdk.core.types import (
    EntryStatus,
    Headers,
    JSONData,
    Mode,
    ModelPreference,
    QueryParams,
    SearchFocus,
    SSEEventType,
)

__all__ = [
    # Exceptions
    "PerplexitySDKError",
    "TransportError",
    "AuthenticationError",
    "RateLimitError",
    "StreamingError",
    "ValidationError",
    # Protocols
    "Transport",
    "StreamParser",
    # Types
    "Headers",
    "QueryParams",
    "JSONData",
    "Mode",
    "SearchFocus",
    "ModelPreference",
    "EntryStatus",
    "SSEEventType",
]
