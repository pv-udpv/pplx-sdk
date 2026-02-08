# GitHub Copilot Instructions for pplx-sdk

## Project Overview

**pplx-sdk** is a production-grade Python SDK for Perplexity AI with SSE streaming and OpenAI compatibility.

### Core Principles

1. **Type Safety First**: All code must pass `mypy --strict`
2. **Layered Architecture**: core → shared → transport/domain → client
3. **Protocol-Oriented**: Use Protocols for abstractions, not ABC
4. **Explicit Errors**: Custom exception hierarchy, no generic Exceptions
5. **Python 3.12+**: Target Python 3.12+ only

## Architecture Layers

### 1. Core (`pplx_sdk/core/`)
- **Purpose**: Protocols, types, exceptions
- **Dependencies**: None (lowest layer)
- **Files**: `protocols.py`, `types.py`, `exceptions.py`
- **Example**:
  ```python
  from pplx_sdk.core.protocols import Transport
  from pplx_sdk.core.exceptions import TransportError
  ```

### 2. Shared (`pplx_sdk/shared/`)
- **Purpose**: Reusable utilities (auth, logging, retry)
- **Dependencies**: `core/`
- **Example**:
  ```python
  from pplx_sdk.shared.retry import retry_with_backoff, RetryConfig
  ```

### 3. Transport (`pplx_sdk/transport/`)
- **Purpose**: HTTP/SSE backends (httpx, curl_cffi)
- **Dependencies**: `core/`, `shared/`
- **Pattern**: Each transport implements `Transport` protocol

### 4. Domain (`pplx_sdk/domain/`)
- **Purpose**: Business logic (threads, entries, collections)
- **Dependencies**: `core/`, `shared/`, `transport/`
- **Pattern**: Service classes with injected transport

### 5. Client (`pplx_sdk/client.py`)
- **Purpose**: High-level API (`PerplexityClient`, `Conversation`)
- **Dependencies**: All layers

## Code Style & Standards

### Type Annotations

**Always include**:
```python
from __future__ import annotations

from typing import Optional, Dict, Any
from pplx_sdk.core.types import Headers, JSONData

def my_function(
    path: str,
    headers: Optional[Headers] = None,
    data: Optional[JSONData] = None,
) -> str:
    ...
```

### Imports
- Use `from __future__ import annotations` at top of modules
- Standard library → typing → external packages → local imports
- `isort` compatible (black profile, line length 100)

### Naming
- Classes: PascalCase (PerplexityClient, SSETransport)
- Functions/methods: snake_case
- Constants: UPPER_SNAKE_CASE
- Private: _leading_underscore

### Error Handling

**Use custom exceptions**:
```python
from pplx_sdk.core.exceptions import TransportError, AuthenticationError

try:
    response = transport.request("GET", "/api/endpoint")
except httpx.HTTPStatusError as exc:
    if exc.response.status_code == 401:
        raise AuthenticationError("Invalid token") from exc
    raise TransportError(f"HTTP {exc.response.status_code}") from exc
```

**Avoid**:
- Bare `except:` or `except Exception:`
- Swallowing exceptions without logging
- Raising generic `Exception` or `ValueError`

### Documentation

**Docstring format** (Google style):
```python
def create_thread(
    title: str,
    access: ThreadAccess = "private",
) -> Thread:
    """Create a new conversation thread.

    Args:
        title: Thread title
        access: Access level (private, org, public)

    Returns:
        Created Thread object

    Raises:
        ValidationError: If title is empty
        TransportError: On API errors
    """
    ...
```

## Testing Patterns

**Structure** (Arrange-Act-Assert):
```python
import pytest
from pplx_sdk.core.exceptions import TransportError

def test_transport_request_success():
    """Test successful HTTP request."""
    # Arrange
    transport = HttpTransport(base_url="https://api.example.com")

    # Act
    with transport:
        response = transport.request("GET", "/health")

    # Assert
    assert response.status_code == 200
```

**Conventions**:
- Descriptive test names: `test_<module>_<behavior>`
- One assertion per test (prefer multiple tests)
- Use `pytest-httpx` for HTTP mocking

## Common Patterns

### Retry with Backoff

```python
from pplx_sdk.shared.retry import retry_with_backoff, RetryConfig
from pplx_sdk.core.exceptions import TransportError

config = RetryConfig(max_retries=3, initial_backoff_ms=1000)

result = retry_with_backoff(
    fetch_data,
    config=config,
    retryable_exceptions=(TransportError,)
)
```

### SSE Streaming

```python
for chunk in stream_ask(...):
    if chunk.type == "answer_chunk":
        print(chunk.text)  # Partial token
    elif chunk.type == "final_response":
        entry = Entry.from_chunk(chunk)  # Full response
```

## Anti-Patterns to Avoid

- **Circular imports**: Don't import client in domain, or domain in transport
- **Mutable default arguments**: Use `Optional[Dict] = None` then `headers = headers or {}`
- **Implicit Any**: Always provide type annotations

## Linting & Formatting

Before committing:
```bash
ruff check --fix .       # Auto-fix linting issues
ruff format .            # Format code
mypy pplx_sdk            # Type check
pytest -v                # Run tests
```
