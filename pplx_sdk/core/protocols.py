"""Core protocols for transport and client abstractions."""

from __future__ import annotations

from typing import Any, ContextManager, Protocol, runtime_checkable

import httpx


@runtime_checkable
class Transport(Protocol):
    """Base transport protocol for HTTP/SSE operations."""

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make HTTP request."""
        ...

    def stream(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ContextManager[httpx.Response]:
        """Make streaming HTTP request."""
        ...


@runtime_checkable
class StreamParser(Protocol):
    """Protocol for SSE event parsing."""

    def parse_event(self, line: str) -> dict[str, Any] | None:
        """Parse SSE event line."""
        ...
