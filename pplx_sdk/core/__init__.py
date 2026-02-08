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
    "AuthenticationError",
    "EntryStatus",
    # Types
    "Headers",
    "JSONData",
    "Mode",
    "ModelPreference",
    # Exceptions
    "PerplexitySDKError",
    "QueryParams",
    "RateLimitError",
    "SSEEventType",
    "SearchFocus",
    "StreamParser",
    "StreamingError",
    # Protocols
    "Transport",
    "TransportError",
    "ValidationError",
]
