---
mode: 'agent'
tools: ['codebase', 'terminalCommand']
description: 'Scaffold a new module in pplx-sdk following the layered architecture pattern with proper typing, tests, and exports'
---

# Scaffold pplx-sdk Module

You are scaffolding a new module for **pplx-sdk**, a production-grade Perplexity AI Python SDK.

## Steps

1. **Identify the target layer** — Determine which architecture layer this module belongs to:
   - `core/` — Protocols, types, exceptions (no dependencies)
   - `shared/` — Reusable utilities like auth, logging, retry (depends on core)
   - `transport/` — HTTP/SSE backends (depends on core, shared)
   - `domain/` — Business logic services (depends on core, shared, transport)
   - `client.py` — High-level API (depends on all layers)

2. **Create the source file** with:
   - `from __future__ import annotations` at the top
   - Complete type annotations on all functions and methods
   - Google-style docstrings with Args, Returns, Raises sections
   - Custom exceptions from `pplx_sdk.core.exceptions`
   - Proper import ordering: stdlib → typing → external → local

3. **Create the test file** in `tests/` with:
   - Matching test file: `tests/test_<layer>_<module>.py`
   - Arrange-Act-Assert pattern
   - Test names: `test_<module>_<behavior>`
   - One primary assertion per test
   - Use `pytest-httpx` for HTTP mocking when needed

4. **Update exports** — Add the new module to the layer's `__init__.py`

5. **Verify** — Run:
   ```bash
   mypy pplx_sdk/ && ruff check pplx_sdk/ tests/ && pytest tests/ -v
   ```

## Template

```python
from __future__ import annotations

from pplx_sdk.core.exceptions import ValidationError
from pplx_sdk.core.protocols import Transport


class MyService:
    """Service for handling [describe purpose].

    Args:
        transport: Transport backend for API communication.
    """

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def my_method(self, param: str, options: dict[str, str] | None = None) -> str:
        """Perform [describe action].

        Args:
            param: Description of param.
            options: Optional configuration overrides.

        Returns:
            Result description.

        Raises:
            ValidationError: If param is empty.
            TransportError: On API communication failure.
        """
        if not param:
            raise ValidationError("param must not be empty")
        opts = options or {}
        response = self._transport.request("GET", f"/api/{param}", headers=opts)
        return response.text
```
