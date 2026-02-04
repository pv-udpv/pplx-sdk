"""Stream manager with retry and reconnection logic.

Provides resilient streaming with automatic retry and resume capabilities.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Generator, Optional

from pplx_sdk.domain.models import MessageChunk
from pplx_sdk.transport.sse import SSETransport


class StreamManager:
    """Manage SSE streams with retry and reconnection.

    Handles automatic retry with exponential backoff and cursor-based
    reconnection for resumable streams.

    Example:
        >>> manager = StreamManager(
        ...     transport,
        ...     max_retries=3,
        ...     retry_backoff_ms=1500
        ... )
        >>> for chunk in manager.stream(query="test", context_uuid="uuid"):
        ...     print(chunk.text)
    """

    def __init__(
        self,
        transport: SSETransport,
        max_retries: int = 3,
        retry_backoff_ms: int = 1500,
        timeout_ms: int = 30000,
    ) -> None:
        """Initialize stream manager.

        Args:
            transport: SSETransport instance
            max_retries: Maximum number of retry attempts
            retry_backoff_ms: Base backoff time in milliseconds
            timeout_ms: Request timeout in milliseconds
        """
        self.transport = transport
        self.max_retries = max_retries
        self.retry_backoff_ms = retry_backoff_ms
        self.timeout_ms = timeout_ms

    def stream(
        self,
        query: str,
        context_uuid: str,
        frontend_uuid: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: Optional[list[str]] = None,
        parent_entry_uuid: Optional[str] = None,
        reconnectable: bool = True,
        **extra: Any,
    ) -> Generator[MessageChunk, None, None]:
        """Stream with automatic retry and reconnection.

        Args:
            query: Search query
            context_uuid: Thread context UUID
            frontend_uuid: Client-generated entry UUID
            mode: Query mode
            model_preference: Model to use
            sources: Source types
            parent_entry_uuid: Parent entry UUID
            reconnectable: Enable reconnection with cursor
            **extra: Additional parameters

        Yields:
            MessageChunk objects from stream

        Raises:
            Exception: If all retries exhausted
        """
        retry_count = 0
        cursor: Optional[str] = None
        resume_entry_uuids: list[str] = []

        while retry_count <= self.max_retries:
            try:
                # Stream from transport
                for chunk in self.transport.stream(
                    query=query,
                    context_uuid=context_uuid,
                    frontend_uuid=frontend_uuid,
                    mode=mode,
                    model_preference=model_preference,
                    sources=sources,
                    parent_entry_uuid=parent_entry_uuid,
                    cursor=cursor,
                    resume_entry_uuids=resume_entry_uuids if resume_entry_uuids else None,
                    **extra,
                ):
                    # Yield chunk
                    yield chunk

                    # Update cursor for reconnection
                    if reconnectable and chunk.cursor:
                        cursor = chunk.cursor

                    # Track backend UUID for resume
                    if chunk.backend_uuid and chunk.backend_uuid not in resume_entry_uuids:
                        resume_entry_uuids.append(chunk.backend_uuid)

                # Stream completed successfully
                break

            except Exception as e:
                retry_count += 1

                # Check if we should retry
                if retry_count > self.max_retries:
                    raise

                # Check if reconnectable
                if not reconnectable or not cursor:
                    raise

                # Calculate backoff time with exponential increase
                backoff_time = self.retry_backoff_ms * (2 ** (retry_count - 1))
                backoff_seconds = backoff_time / 1000.0

                # Yield error chunk
                error_chunk = MessageChunk(
                    type="error",
                    status="retrying",
                    data={
                        "error": str(e),
                        "retry_count": retry_count,
                        "backoff_seconds": backoff_seconds,
                    },
                    backend_uuid=None,
                    context_uuid=context_uuid,
                )
                yield error_chunk

                # Wait before retry
                time.sleep(backoff_seconds)

    def stream_with_timeout(
        self,
        query: str,
        context_uuid: str,
        frontend_uuid: str,
        timeout_ms: Optional[int] = None,
        **kwargs: Any,
    ) -> Generator[MessageChunk, None, None]:
        """Stream with timeout enforcement.

        Args:
            query: Search query
            context_uuid: Thread context UUID
            frontend_uuid: Client-generated entry UUID
            timeout_ms: Override default timeout
            **kwargs: Additional parameters

        Yields:
            MessageChunk objects from stream

        Raises:
            TimeoutError: If stream exceeds timeout
        """
        timeout = (timeout_ms or self.timeout_ms) / 1000.0
        start_time = time.time()

        for chunk in self.stream(
            query=query,
            context_uuid=context_uuid,
            frontend_uuid=frontend_uuid,
            **kwargs,
        ):
            # Check timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Stream exceeded timeout of {timeout}s")

            yield chunk
