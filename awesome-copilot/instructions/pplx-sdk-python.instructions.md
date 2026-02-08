---
description: 'Python SDK development conventions for pplx-sdk — a production-grade Perplexity AI SDK with SSE streaming, layered architecture, and strict type safety'
applyTo: '**/*.py'
---

# pplx-sdk: Perplexity AI Python SDK

## Project Overview

pplx-sdk is a production-grade Python SDK for Perplexity AI featuring native SSE streaming, OpenAI-compatible API wrappers, full entity models, reconnection with retry logic, and async-first architecture.

## Core Principles

1. **Type Safety First** — All code must pass `mypy --strict`. Use `from __future__ import annotations` in every module.
2. **Layered Architecture** — Follow strict dependency ordering: `core → shared → transport → domain → client`.
3. **Protocol-Oriented** — Use `typing.Protocol` for abstractions instead of ABCs.
4. **Explicit Errors** — Use the custom exception hierarchy from `pplx_sdk.core.exceptions`. Never raise bare `Exception` or `ValueError`.
5. **Python 3.12+** — Target Python 3.12+ exclusively. Use modern syntax and stdlib features.

## Architecture Layers

### Core (`pplx_sdk/core/`)
- Protocols, types, exceptions — zero external dependencies.
- Files: `protocols.py`, `types.py`, `exceptions.py`.

### Shared (`pplx_sdk/shared/`)
- Reusable utilities: auth, logging, retry with backoff.
- Depends only on `core/`.

### Transport (`pplx_sdk/transport/`)
- HTTP/SSE backends (httpx, curl_cffi).
- Each transport implements the `Transport` protocol.
- Depends on `core/` and `shared/`.

### Domain (`pplx_sdk/domain/`)
- Business logic: threads, entries, collections.
- Service classes with injected transport.
- Depends on `core/`, `shared/`, `transport/`.

### Client (`pplx_sdk/client.py`)
- High-level API: `PerplexityClient`, `Conversation`.
- Depends on all layers.

## Code Standards

### Type Annotations
- Always use `from __future__ import annotations` at the top of modules.
- Import order: stdlib → typing → external packages → local imports.
- Use `Optional[X]` instead of `X | None` for function parameters with default `None`.
- Provide complete return type annotations.

### Naming Conventions
- Classes: `PascalCase` (`PerplexityClient`, `SSETransport`)
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Error Handling
- Use custom exceptions: `TransportError`, `AuthenticationError`, `ValidationError`.
- Always chain exceptions with `raise ... from exc`.
- Never swallow exceptions without logging.

### Documentation
- Google-style docstrings with `Args`, `Returns`, `Raises` sections.
- Every public API must have a docstring.

### Testing
- Use `pytest` with `pytest-httpx` for HTTP mocking and `pytest-asyncio` for async tests.
- Follow Arrange-Act-Assert pattern.
- Test names: `test_<module>_<behavior>`.
- One primary assertion per test.

## SSE Streaming Patterns
- Parse SSE format: `event:` and `data:` lines, blank line separates events.
- Handle `answer_chunk` (partial tokens) and `final_response` (complete entry) event types.
- Use cursor-based resumption for reconnection.
- Apply `RetryConfig` with exponential backoff for transient failures.

## Linting & Formatting
- Use `ruff check --fix .` for linting and `ruff format .` for formatting.
- Run `mypy pplx_sdk/` for type checking.
- Run `pytest tests/ -v` for testing.

## Anti-Patterns to Avoid
- Circular imports between layers.
- Mutable default arguments — use `Optional[Dict] = None` then `headers = headers or {}`.
- Implicit `Any` — always provide type annotations.
- Bare `except:` or `except Exception:`.
- Importing client in domain, or domain in transport.
