"""Perplexity AI SDK.

Python SDK for Perplexity AI with REST API wrappers and OpenAI-compatible API layer.
"""

__version__ = "0.1.0"
__author__ = "pv-udpv"

from pplx_sdk.client import AsyncPplxClient, PplxClient
from pplx_sdk.models import (
    Chat,
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionRole,
    CompletionUsage,
    Delta,
)

__all__ = [
    "PplxClient",
    "AsyncPplxClient",
    # Models
    "ChatCompletionRole",
    "ChatCompletionMessage",
    "Chat",
    "ChatCompletion",
    "ChatCompletionChunk",
    "Delta",
    "CompletionUsage",
]
