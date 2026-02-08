---
description: "Scaffold a new module or component for pplx-sdk"
name: "scaffold"
argument-hint: "Describe what to scaffold (e.g., 'new transport backend', 'domain service for spaces')"
---

Scaffold a new component following pplx-sdk architecture:

## Architecture Rules

- **core/**: Protocols, types, exceptions — no external dependencies
- **shared/**: Reusable utilities — depends only on `core/`
- **transport/**: HTTP/SSE backends — depends on `core/`, `shared/`
- **domain/**: Business logic services — depends on `core/`, `shared/`, `transport/`
- **client.py**: High-level API — depends on all layers

## Scaffold Template

For each new module, generate:

1. **Source file** with:
   - `from __future__ import annotations`
   - Complete type annotations
   - Google-style docstrings
   - Custom exception handling using `pplx_sdk.core.exceptions`

2. **Test file** (`tests/test_<module>.py`) with:
   - Arrange-Act-Assert structure
   - `pytest-httpx` mocks where needed
   - Coverage for success, error, and edge cases

3. **`__init__.py` update** with public exports

## Example: New Transport

```python
# pplx_sdk/transport/new_backend.py
from __future__ import annotations

from typing import Any, ContextManager, Dict, Optional

from pplx_sdk.core.exceptions import TransportError


class NewBackendTransport:
    """Transport using new-backend for HTTP requests.

    Example:
        >>> transport = NewBackendTransport(base_url="https://api.example.com")
        >>> with transport:
        ...     response = transport.request("GET", "/health")
    """

    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        ...
```
