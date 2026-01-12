"""SSE (Server-Sent Events) transport for streaming responses.

Handles SSE protocol parsing and yields MessageChunk objects.
"""

import json
from typing import Any, Dict, Generator, Optional

import httpx

from pplx_sdk.domain.models import MessageChunk


class SSETransport:
    """SSE streaming transport for Perplexity API.

    Parses Server-Sent Events format and yields MessageChunk objects.
    Handles the SSE protocol including event types, data fields, and end markers.

    SSE Format:
        event: event_type
        data: {"json": "data"}

        : comment or [end] marker

    Example:
        >>> transport = SSETransport(client, "/rest/sse/perplexity.ask")
        >>> for chunk in transport.stream(query="test", context_uuid="uuid"):
        ...     print(chunk.type, chunk.data)
    """

    def __init__(self, client: httpx.Client, endpoint: str) -> None:
        """Initialize SSE transport.

        Args:
            client: httpx.Client instance for making requests
            endpoint: SSE endpoint path (e.g., /rest/sse/perplexity.ask)
        """
        self.client = client
        self.endpoint = endpoint

    def stream(
        self,
        query: str,
        context_uuid: str,
        frontend_uuid: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: Optional[list[str]] = None,
        parent_entry_uuid: Optional[str] = None,
        cursor: Optional[str] = None,
        resume_entry_uuids: Optional[list[str]] = None,
        **extra: Any,
    ) -> Generator[MessageChunk, None, None]:
        """Stream SSE events from Perplexity API.

        Args:
            query: Search query string
            context_uuid: Thread context UUID
            frontend_uuid: Client-generated entry UUID
            mode: Query mode (concise, research, etc.)
            model_preference: Model to use (pplx-70b-chat, etc.)
            sources: List of source types to use
            parent_entry_uuid: Parent entry for threaded queries
            cursor: Resume cursor for reconnection
            resume_entry_uuids: Entry UUIDs to resume from
            **extra: Additional request parameters

        Yields:
            MessageChunk objects parsed from SSE events

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        # Build request payload
        payload: Dict[str, Any] = {
            "query_str": query,
            "context_uuid": context_uuid,
            "frontend_uuid": frontend_uuid,
            "mode": mode,
            "model_preference": model_preference,
            "sources": sources or ["web"],
            "use_schematized_api": True,
            "language": "en-US",
            "timezone": "UTC",
            "is_incognito": False,
        }

        if parent_entry_uuid:
            payload["parent_entry_uuid"] = parent_entry_uuid

        if cursor:
            payload["cursor"] = cursor

        if resume_entry_uuids:
            payload["resume_entry_uuids"] = resume_entry_uuids

        # Add any extra parameters
        payload.update(extra)

        # Make streaming request
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
        }

        with self.client.stream("POST", self.endpoint, json=payload, headers=headers) as response:
            response.raise_for_status()

            # Parse SSE stream
            event_type: Optional[str] = None
            data_buffer: list[str] = []

            for line in response.iter_lines():
                line = line.strip()

                # Skip empty lines and comments (except [end] marker)
                if not line:
                    # Empty line indicates end of event
                    if event_type and data_buffer:
                        yield self._parse_event(event_type, "".join(data_buffer))
                        event_type = None
                        data_buffer = []
                    continue

                if line.startswith(":"):
                    # Check for end marker
                    if "[end]" in line:
                        break
                    continue

                # Parse SSE fields
                if ":" in line:
                    field, _, value = line.partition(":")
                    value = value.lstrip()

                    if field == "event":
                        event_type = value
                    elif field == "data":
                        data_buffer.append(value)

            # Handle any remaining buffered event
            if event_type and data_buffer:
                yield self._parse_event(event_type, "".join(data_buffer))

    def _parse_event(self, event_type: str, data: str) -> MessageChunk:
        """Parse SSE event into MessageChunk.

        Args:
            event_type: Event type (query_progress, answer_chunk, etc.)
            data: JSON data string

        Returns:
            MessageChunk object
        """
        # Parse JSON data
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            parsed_data = {"text": data}

        # Extract common fields
        backend_uuid = parsed_data.get("backend_uuid")
        context_uuid = parsed_data.get("context_uuid")
        status = parsed_data.get("status")
        text = parsed_data.get("text")
        cursor = parsed_data.get("cursor")

        return MessageChunk(
            type=event_type,
            status=status,
            data=parsed_data,
            backend_uuid=backend_uuid,
            context_uuid=context_uuid,
            text=text,
            cursor=cursor,
            reconnectable=cursor is not None,
        )
