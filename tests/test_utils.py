"""Tests for utility functions."""

import pytest

from pplx_sdk.utils.auth import (
    extract_token_from_cookies,
    extract_token_from_header,
    get_token_from_env,
)


def test_extract_token_from_cookies() -> None:
    """Test token extraction from cookie string."""
    # Test with pplx.session-id
    cookies = "pplx.session-id=abc123; other=value"
    token = extract_token_from_cookies(cookies)
    assert token == "abc123"

    # Test with pplx_session
    cookies = "pplx_session=def456; other=value"
    token = extract_token_from_cookies(cookies)
    assert token == "def456"

    # Test with no matching cookie
    cookies = "other=value; another=test"
    token = extract_token_from_cookies(cookies)
    assert token is None


def test_extract_token_from_header() -> None:
    """Test token extraction from Authorization header."""
    # Test with Bearer token
    header = "Bearer abc123"
    token = extract_token_from_header(header)
    assert token == "abc123"

    # Test with plain token
    header = "xyz789"
    token = extract_token_from_header(header)
    assert token == "xyz789"

    # Test with empty header
    token = extract_token_from_header("")
    assert token is None

    # Test with None
    token = extract_token_from_header(None)  # type: ignore
    assert token is None


def test_get_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test token retrieval from environment variables."""
    # Test with PPLX_AUTH_TOKEN
    monkeypatch.setenv("PPLX_AUTH_TOKEN", "token123")
    token = get_token_from_env()
    assert token == "token123"

    # Clear and test with PPLX_SESSION_TOKEN
    monkeypatch.delenv("PPLX_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("PPLX_SESSION_TOKEN", "token456")
    token = get_token_from_env()
    assert token == "token456"

    # Test with no env vars set
    monkeypatch.delenv("PPLX_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("PPLX_SESSION_TOKEN", raising=False)
    monkeypatch.delenv("PERPLEXITY_AUTH_TOKEN", raising=False)
    token = get_token_from_env()
    assert token is None
