"""Core protocols for transport and client abstractions."""

from __future__ import annotations

from typing import Any, ContextManager, Dict, Optional, Protocol, runtime_checkable

import httpx


@runtime_checkable
class Transport(Protocol):
    """Base transport protocol for HTTP/SSE operations."""

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make HTTP request."""
        ...

    def stream(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ContextManager[httpx.Response]:
        """Make streaming HTTP request."""
        ...


@runtime_checkable
class StreamParser(Protocol):
    """Protocol for SSE event parsing."""

    def parse_event(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse SSE event line."""
        ...
