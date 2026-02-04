"""OpenAI-compatible API layer for Perplexity AI.

Exposes Perplexity AI as an OpenAI-compatible endpoint suitable for use with
OpenAI client libraries and tools that expect OpenAI API compatibility.
"""

import json
import logging
from typing import AsyncGenerator, Generator

from pydantic import BaseModel

from pplx_sdk.client import AsyncPplxClient, PplxClient
from pplx_sdk.models import ChatCompletionMessage, ChatCompletionRole

logger = logging.getLogger(__name__)


class OpenAICompatibleLayer:
    """Adapter that makes Perplexity AI compatible with OpenAI SDK."""

    def __init__(self, pplx_client: PplxClient):
        """Initialize OpenAI compatible layer.

        Args:
            pplx_client: Initialized PplxClient instance
        """
        self.pplx_client = pplx_client

    def create_completion(
        self, model: str, messages: list[dict], stream: bool = False, **kwargs
    ) -> dict | Generator[str, None, None]:
        """Create completion compatible with OpenAI API.

        Args:
            model: Model name
            messages: List of message dicts with role and content
            stream: Whether to stream
            **kwargs: Additional parameters

        Returns:
            Completion response dict or generator of chunks
        """
        # Convert messages to SDK format
        pplx_messages = [
            ChatCompletionMessage(role=ChatCompletionRole(msg["role"]), content=msg["content"])
            for msg in messages
        ]

        # Call SDK
        result = self.pplx_client.chat_complete(
            messages=pplx_messages,
            model=model,
            stream=stream,
            **kwargs,
        )

        if stream:
            return self._stream_wrapper(result)
        return self._response_wrapper(result)

    def _response_wrapper(self, response) -> dict:
        """Convert SDK response to OpenAI format."""
        return response.model_dump()

    def _stream_wrapper(self, stream) -> Generator[str, None, None]:
        """Wrap streaming response as OpenAI format."""
        for chunk in stream:
            data = chunk.model_dump()
            yield f"data: {json.dumps(data)}\n\n"


class AsyncOpenAICompatibleLayer:
    """Async adapter that makes Perplexity AI compatible with OpenAI SDK."""

    def __init__(self, pplx_client: AsyncPplxClient):
        """Initialize async OpenAI compatible layer.

        Args:
            pplx_client: Initialized AsyncPplxClient instance
        """
        self.pplx_client = pplx_client

    async def create_completion(
        self, model: str, messages: list[dict], stream: bool = False, **kwargs
    ) -> dict | AsyncGenerator[str, None]:
        """Create completion compatible with OpenAI API.

        Args:
            model: Model name
            messages: List of message dicts with role and content
            stream: Whether to stream
            **kwargs: Additional parameters

        Returns:
            Completion response dict or async generator of chunks
        """
        # Convert messages to SDK format
        pplx_messages = [
            ChatCompletionMessage(role=ChatCompletionRole(msg["role"]), content=msg["content"])
            for msg in messages
        ]

        # Call SDK
        result = await self.pplx_client.chat_complete(
            messages=pplx_messages,
            model=model,
            stream=stream,
            **kwargs,
        )

        if stream:
            return self._stream_wrapper(result)
        return self._response_wrapper(result)

    def _response_wrapper(self, response) -> dict:
        """Convert SDK response to OpenAI format."""
        return response.model_dump()

    async def _stream_wrapper(self, stream) -> AsyncGenerator[str, None]:
        """Wrap streaming response as OpenAI format."""
        async for chunk in stream:
            data = chunk.model_dump()
            yield f"data: {json.dumps(data)}\n\n"
