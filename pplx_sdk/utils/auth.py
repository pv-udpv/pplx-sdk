"""Authentication helpers for token extraction."""

import os
from typing import Optional


def extract_token_from_cookies(cookie_string: str) -> Optional[str]:
    """Extract Perplexity session token from cookie string.

    Args:
        cookie_string: Cookie string (e.g., from browser DevTools)

    Returns:
        Session token if found, None otherwise

    Example:
        >>> cookies = "pplx.session-id=abc123; other=value"
        >>> token = extract_token_from_cookies(cookies)
        >>> print(token)
        'abc123'
    """
    # Parse cookie string
    for cookie in cookie_string.split(";"):
        cookie = cookie.strip()
        if "=" in cookie:
            key, value = cookie.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Look for common session token keys
            if key in ("pplx.session-id", "pplx_session", "session-id", "session"):
                return value

    return None


def get_token_from_env() -> Optional[str]:
    """Get authentication token from environment variables.

    Checks multiple environment variable names in order:
    - PPLX_AUTH_TOKEN
    - PPLX_SESSION_TOKEN
    - PERPLEXITY_AUTH_TOKEN

    Returns:
        Token if found, None otherwise
    """
    for env_var in ("PPLX_AUTH_TOKEN", "PPLX_SESSION_TOKEN", "PERPLEXITY_AUTH_TOKEN"):
        token = os.getenv(env_var)
        if token:
            return token

    return None


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """Extract token from Authorization header.

    Args:
        auth_header: Authorization header value

    Returns:
        Token if found, None otherwise

    Example:
        >>> header = "Bearer abc123"
        >>> token = extract_token_from_header(header)
        >>> print(token)
        'abc123'
    """
    if not auth_header:
        return None

    # Handle Bearer token
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    # Handle plain token
    return auth_header
