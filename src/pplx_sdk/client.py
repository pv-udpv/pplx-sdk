"""Perplexity AI client implementations."""

import json
import logging
from typing import AsyncGenerator, Generator, Optional

import httpx
from pydantic import ValidationError

from pplx_sdk.config import PplxSettings
from pplx_sdk.models import Chat, ChatCompletion, ChatCompletionChunk, ChatCompletionMessage

logger = logging.getLogger(__name__)


class PplxClient:
    """Synchronous Perplexity AI client."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: dict) -> None:
        """Initialize PplxClient.

        Args:
            api_key: API key for Perplexity AI (overrides env var)
            **kwargs: Additional configuration options
        """
        self.config = PplxSettings(api_key=api_key, **kwargs)
        self.client = httpx.Client(
            base_url=self.config.api_base,
            headers=self._get_headers(),
            timeout=self.config.api_timeout,
            verify=self.config.verify_ssl,
        )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def chat_complete(
        self,
        messages: list[ChatCompletionMessage],
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> ChatCompletion | Generator[ChatCompletionChunk, None, None]:
        """Create chat completion.

        Args:
            messages: Chat messages
            model: Model name (uses default if not specified)
            stream: Whether to stream response
            **kwargs: Additional parameters

        Returns:
            ChatCompletion or generator of ChatCompletionChunk if streaming
        """
        model = model or self.config.default_chat_model
        payload = Chat(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs,
        )

        if stream:
            return self._stream_chat_complete(payload)
        return self._chat_complete(payload)

    def _chat_complete(self, payload: Chat) -> ChatCompletion:
        """Internal non-streaming chat completion."""
        response = self.client.post(
            "/chat/completions",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()
        return ChatCompletion(**response.json())

    def _stream_chat_complete(
        self, payload: Chat
    ) -> Generator[ChatCompletionChunk, None, None]:
        """Internal streaming chat completion."""
        with self.client.stream(
            "POST",
            "/chat/completions",
            content=payload.model_dump_json(),
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or line.startswith(":"):
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        yield ChatCompletionChunk(**data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Failed to parse chunk: {e}")

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncPplxClient:
    """Asynchronous Perplexity AI client."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: dict) -> None:
        """Initialize AsyncPplxClient.

        Args:
            api_key: API key for Perplexity AI (overrides env var)
            **kwargs: Additional configuration options
        """
        self.config = PplxSettings(api_key=api_key, **kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.config.api_base,
            headers=self._get_headers(),
            timeout=self.config.api_timeout,
            verify=self.config.verify_ssl,
        )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def chat_complete(
        self,
        messages: list[ChatCompletionMessage],
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> ChatCompletion | AsyncGenerator[ChatCompletionChunk, None]:
        """Create chat completion.

        Args:
            messages: Chat messages
            model: Model name (uses default if not specified)
            stream: Whether to stream response
            **kwargs: Additional parameters

        Returns:
            ChatCompletion or async generator of ChatCompletionChunk if streaming
        """
        model = model or self.config.default_chat_model
        payload = Chat(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs,
        )

        if stream:
            return self._stream_chat_complete(payload)
        return await self._chat_complete(payload)

    async def _chat_complete(self, payload: Chat) -> ChatCompletion:
        """Internal non-streaming chat completion."""
        response = await self.client.post(
            "/chat/completions",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()
        return ChatCompletion(**response.json())

    async def _stream_chat_complete(
        self, payload: Chat
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Internal streaming chat completion."""
        async with self.client.stream(
            "POST",
            "/chat/completions",
            content=payload.model_dump_json(),
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or line.startswith(":"):
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        yield ChatCompletionChunk(**data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.warning(f"Failed to parse chunk: {e}")

    async def close(self) -> None:
        """Close the client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
