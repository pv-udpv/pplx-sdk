"""HTTP transport layer using httpx.

Provides a wrapper around httpx.Client with authentication and configuration.
"""

from typing import Any, Dict, Optional

import httpx


class HttpTransport:
    """HTTP transport wrapper for Perplexity API.

    Wraps httpx.Client with authentication headers and base URL configuration.
    Supports both synchronous requests and streaming.

    Example:
        >>> transport = HttpTransport(
        ...     base_url="https://www.perplexity.ai",
        ...     auth_token="session-token",
        ...     timeout=30.0
        ... )
        >>> with transport:
        ...     response = transport.request("GET", "/api/endpoint")
    """

    def __init__(
        self,
        base_url: str = "https://www.perplexity.ai",
        auth_token: Optional[str] = None,
        timeout: float = 30.0,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize HTTP transport.

        Args:
            base_url: Base URL for API requests
            auth_token: Authentication token (session ID)
            timeout: Request timeout in seconds
            default_headers: Additional headers to include in all requests
        """
        self.base_url = base_url
        self.timeout = timeout

        # Build default headers
        headers = {
            "User-Agent": "pplx-sdk/0.1.0",
            "X-Client-Name": "web",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        if default_headers:
            headers.update(default_headers)

        self.default_headers = headers
        self.client: Optional[httpx.Client] = None

    def __enter__(self) -> "HttpTransport":
        """Context manager entry."""
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.default_headers,
            follow_redirects=True,
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self.client:
            self.client.close()
            self.client = None

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (relative to base_url)
            params: Query parameters
            json: JSON request body
            headers: Additional headers for this request

        Returns:
            httpx.Response object

        Raises:
            RuntimeError: If transport not used in context manager
            httpx.HTTPError: On HTTP errors
        """
        if not self.client:
            raise RuntimeError("HttpTransport must be used as context manager")

        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)

        return self.client.request(
            method=method,
            url=path,
            params=params,
            json=json,
            headers=merged_headers,
        )

    def stream(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make a streaming HTTP request.

        Args:
            method: HTTP method (typically POST for SSE)
            path: Request path
            json: JSON request body
            headers: Additional headers for this request

        Returns:
            httpx.Response with streaming enabled

        Raises:
            RuntimeError: If transport not used in context manager
            httpx.HTTPError: On HTTP errors
        """
        if not self.client:
            raise RuntimeError("HttpTransport must be used as context manager")

        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)

        # Override content-type and accept for SSE
        if "Accept" not in merged_headers:
            merged_headers["Accept"] = "text/event-stream"

        return self.client.stream(
            method=method,
            url=path,
            json=json,
            headers=merged_headers,
        )
