"""Entries service for managing question-answer entries.

Provides high-level API for asking questions and streaming responses.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from typing import Any

from pplx_sdk.domain.models import Entry, MessageChunk, StreamStatus
from pplx_sdk.transport.sse import SSETransport


class EntriesService:
    """Service for managing entries (Q&A pairs).

    Handles question-asking with SSE streaming and synchronous wrappers.

    Example:
        >>> entries = EntriesService(transport)
        >>> for chunk in entries.stream_ask("What is AI?", context_uuid="uuid"):
        ...     print(chunk.text, end="")
        >>> entry = entries.ask("What is AI?", context_uuid="uuid")
        >>> print(entry.text_completed)

    """

    def __init__(self, sse_transport: SSETransport) -> None:
        """Initialize entries service.

        Args:
            sse_transport: SSETransport instance for streaming

        """
        self.transport = sse_transport

    def stream_ask(
        self,
        query: str,
        context_uuid: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: list[str] | None = None,
        parent_entry_uuid: str | None = None,
        frontend_uuid: str | None = None,
        **extra: Any,
    ) -> Generator[MessageChunk, None, None]:
        """Stream a question and yield SSE events.

        Args:
            query: Question to ask
            context_uuid: Thread context UUID
            mode: Query mode (concise, research, etc.)
            model_preference: Model to use
            sources: List of source types
            parent_entry_uuid: Parent entry for threaded queries
            frontend_uuid: Client-generated entry UUID (auto-generated if not provided)
            **extra: Additional parameters

        Yields:
            MessageChunk objects from SSE stream

        Raises:
            httpx.HTTPError: On HTTP errors

        """
        # Generate frontend UUID if not provided
        if not frontend_uuid:
            frontend_uuid = str(uuid.uuid4())

        # Stream from transport
        yield from self.transport.stream(
            query=query,
            context_uuid=context_uuid,
            frontend_uuid=frontend_uuid,
            mode=mode,
            model_preference=model_preference,
            sources=sources,
            parent_entry_uuid=parent_entry_uuid,
            **extra,
        )

    def ask(
        self,
        query: str,
        context_uuid: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: list[str] | None = None,
        parent_entry_uuid: str | None = None,
        frontend_uuid: str | None = None,
        **extra: Any,
    ) -> Entry:
        """Ask a question and return the complete entry.

        This is a synchronous wrapper that collects the full stream.

        Args:
            query: Question to ask
            context_uuid: Thread context UUID
            mode: Query mode
            model_preference: Model to use
            sources: List of source types
            parent_entry_uuid: Parent entry for threaded queries
            frontend_uuid: Client-generated entry UUID
            **extra: Additional parameters

        Returns:
            Complete Entry object

        Raises:
            httpx.HTTPError: On HTTP errors
            ValueError: If stream fails or no final response received

        """
        # Generate frontend UUID if not provided
        if not frontend_uuid:
            frontend_uuid = str(uuid.uuid4())

        # Collect stream
        entry_data: dict[str, Any] = {
            "frontend_uuid": frontend_uuid,
            "context_uuid": context_uuid,
            "query": query,
            "status": StreamStatus.PENDING,
            "text_completed": False,
            "blocks": [],
            "sources": [],
        }

        text_chunks: list[str] = []

        for chunk in self.stream_ask(
            query=query,
            context_uuid=context_uuid,
            mode=mode,
            model_preference=model_preference,
            sources=sources,
            parent_entry_uuid=parent_entry_uuid,
            frontend_uuid=frontend_uuid,
            **extra,
        ):
            # Accumulate text chunks
            if chunk.text:
                text_chunks.append(chunk.text)

            # Update from final_response
            if chunk.type == "final_response":
                entry_data.update(
                    {
                        "backend_uuid": chunk.data.get("backend_uuid", ""),
                        "status": StreamStatus.COMPLETED,
                        "text_completed": True,
                        "display_model": chunk.data.get("display_model"),
                        "cursor": chunk.data.get("cursor"),
                    }
                )

                # Extract blocks if present
                if "blocks" in chunk.data:
                    entry_data["blocks"] = chunk.data["blocks"]

                # Extract sources if present
                if "sources" in chunk.data:
                    entry_data["sources"] = chunk.data["sources"]

            # Handle error
            if chunk.type == "error":
                entry_data["status"] = StreamStatus.FAILED

        # Ensure backend_uuid is present
        if "backend_uuid" not in entry_data:
            raise ValueError("No final_response received from stream")

        # Create and return entry
        return Entry(**entry_data)
