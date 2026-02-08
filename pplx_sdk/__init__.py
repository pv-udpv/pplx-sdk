"""Perplexity AI Python SDK with OpenAI-compatible API.

Quick start:
    from pplx_sdk import PerplexityClient, Conversation

    client = PerplexityClient(auth_token="<session-token>")
    conv = client.new_conversation(title="Research")

    for chunk in conv.ask_stream("Explain quantum computing"):
        print(chunk.text, end="", flush=True)
"""

from pplx_sdk.client import Conversation, PerplexityClient
from pplx_sdk.core.exceptions import (
    AuthenticationError,
    PerplexitySDKError,
    RateLimitError,
    StreamingError,
    TransportError,
    ValidationError,
)
from pplx_sdk.domain.models import Entry, MessageChunk, Thread

__version__ = "0.1.0"
__author__ = "Perplexity AI Reverse Engineers"
__license__ = "MIT"

__all__ = [
    "AuthenticationError",
    "Conversation",
    "Entry",
    "MessageChunk",
    "PerplexityClient",
    # Exceptions
    "PerplexitySDKError",
    "RateLimitError",
    "StreamingError",
    "Thread",
    "TransportError",
    "ValidationError",
]
