"""Tests for transport layer (HTTP and SSE)."""

import pytest
from pytest_httpx import HTTPXMock

from pplx_sdk.transport.http import HttpTransport


def test_http_transport_initialization(mock_auth_token: str) -> None:
    """Test HTTP transport initialization."""
    transport = HttpTransport(
        base_url="https://api.test.com",
        auth_token=mock_auth_token,
        timeout=30.0,
    )

    assert transport.base_url == "https://api.test.com"
    assert transport.timeout == 30.0
    assert "Authorization" in transport.default_headers
    assert transport.default_headers["Authorization"] == f"Bearer {mock_auth_token}"


def test_http_transport_context_manager(mock_auth_token: str) -> None:
    """Test HTTP transport context manager."""
    transport = HttpTransport(auth_token=mock_auth_token)

    with transport:
        assert transport.client is not None

    assert transport.client is None


def test_http_transport_request(httpx_mock: HTTPXMock, mock_auth_token: str) -> None:
    """Test HTTP transport makes requests correctly."""
    httpx_mock.add_response(
        url="https://www.perplexity.ai/api/test",
        json={"status": "success", "data": "test"},
    )

    transport = HttpTransport(auth_token=mock_auth_token)

    with transport:
        response = transport.request("GET", "/api/test")
        assert response.status_code == 200
        assert response.json()["status"] == "success"


def test_http_transport_request_without_context_manager(mock_auth_token: str) -> None:
    """Test HTTP transport raises error when not in context manager."""
    transport = HttpTransport(auth_token=mock_auth_token)

    with pytest.raises(RuntimeError, match="must be used as context manager"):
        transport.request("GET", "/api/test")


def test_http_transport_custom_headers(httpx_mock: HTTPXMock, mock_auth_token: str) -> None:
    """Test HTTP transport with custom headers."""
    httpx_mock.add_response(
        url="https://www.perplexity.ai/api/test",
        json={"status": "success"},
    )

    custom_headers = {"X-Custom-Header": "custom-value"}
    transport = HttpTransport(
        auth_token=mock_auth_token,
        default_headers=custom_headers,
    )

    with transport:
        response = transport.request("GET", "/api/test")
        assert response.status_code == 200

        # Verify custom header is included
        assert "X-Custom-Header" in transport.default_headers
        assert transport.default_headers["X-Custom-Header"] == "custom-value"
