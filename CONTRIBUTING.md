# Contributing to pplx-sdk

Thank you for interest in contributing! This guide will help you get started.

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Development Environment

```bash
# Clone repository
git clone https://github.com/pv-udpv/pplx-sdk
cd pplx-sdk

# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with development dependencies
uv pip install -e ".[dev]"

# Verify setup
python -c "import pplx_sdk; print(pplx_sdk.__version__)"
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/issue-123
```

### 2. Make Changes

Follow these standards:

#### Code Style
- **Type hints**: 100% coverage (mypy --strict)
- **Docstrings**: Google style on all public APIs
- **Line length**: 100 characters (ruff config)
- **Imports**: isort + black compatible

#### Example Function

```python
from typing import Optional

def stream_ask(
    self,
    query: str,
    context_uuid: str,
    mode: Optional[str] = None,
    **kwargs: Any,
) -> Generator[MessageChunk, None, None]:
    """Stream response from Perplexity API.

    Args:
        query: User query string.
        context_uuid: Thread UUID.
        mode: Query mode (research, concise, etc).
        **kwargs: Additional parameters.

    Yields:
        MessageChunk events from SSE stream.

    Raises:
        TimeoutError: If stream exceeds timeout_ms.
        RuntimeError: If stream is empty.
    """
    # Implementation
    ...
```

### 3. Format & Lint

```bash
# Format code
ruff format .

# Run linter
ruff check --fix .

# Type check
mypy pplx_sdk

# All-in-one
make lint  # if Makefile exists
```

### 4. Write Tests

```bash
# Create test_my_feature.py in tests/
# Run tests
pytest tests/test_my_feature.py -v

# Run all tests
pytest tests/ -v --cov=pplx_sdk

# Check coverage
pytest tests/ --cov=pplx_sdk --cov-report=html
# Open htmlcov/index.html
```

### 5. Commit & Push

```bash
# Commit with clear message
git add .
git commit -m "feat: add streaming manager with retry logic"

# or
git commit -m "fix: handle SSE parse errors gracefully"

# Commit message types:
# feat: New feature
# fix: Bug fix
# docs: Documentation
# test: Test additions
# refactor: Code refactoring
# chore: Build, deps, etc

# Push
git push origin feature/my-feature
```

### 6. Open Pull Request

- Link to related issues (#123)
- Include test results
- Screenshot/example if UI changes
- Follow template

## Testing

### Unit Tests

```bash
# Run specific test
pytest tests/test_transport.py::test_http_request -v

# Run with coverage
pytest tests/ --cov=pplx_sdk --cov-report=term-missing

# Run async tests
pytest tests/test_streaming.py -v
```

### Using pytest-httpx for Mocking

```python
import pytest
from pytest_httpx import HTTPXMock
from pplx_sdk.transport import HttpTransport

def test_http_request(httpx_mock: HTTPXMock) -> None:
    """Test HTTP transport with mocked response."""
    httpx_mock.add_response(json={"result": "success"})
    
    transport = HttpTransport()
    response = transport.request("GET", "test")
    
    assert response.json() == {"result": "success"}
```

### Using pytest Fixtures

```python
# tests/fixtures.py
@pytest.fixture
def mock_sse_response() -> str:
    """Mock SSE streaming response."""
    return """event: answer_chunk
data: {"type": "answer_chunk", "text": "Hello"}

event: answer_chunk
data: {"type": "answer_chunk", "text": " world"}

event: final_response
data: {"type": "final_response", "backend_uuid": "uuid", "text_completed": true}

: [end]
"""
```

## Code Organization

### Module Structure

```
pplx_sdk/
├── __init__.py                 # Public API
├── client.py                   # PerplexityClient, Conversation
├── domain/
│   ├── __init__.py
│   ├── models.py              # Pydantic data classes
│   ├── entries.py             # EntriesService (core Ask API)
│   ├── threads.py             # ThreadsService
│   ├── collections.py         # CollectionsService
│   ├── memories.py            # MemoriesService
│   └── articles.py            # ArticlesService
├── transport/
│   ├── __init__.py
│   ├── http.py                # HttpTransport wrapper
│   └── sse.py                 # SSE streaming
├── streaming/
│   ├── __init__.py
│   ├── manager.py             # StreamManager (retry/reconnect)
│   ├── parser.py              # SSE utilities
│   └── types.py               # Type definitions
├── api/
│   ├── __init__.py
│   ├── oai_server.py          # FastAPI OpenAI adapter
│   ├── oai_models.py          # OpenAI Pydantic models
│   └── middleware.py          # Auth, logging
└── utils/
    ├── __init__.py
    ├── auth.py                # Token extraction
    └── logging.py             # Structured logging
```

## Common Issues

### mypy Errors

```bash
# Check strict mode
mypy pplx_sdk --strict

# Ignore specific errors
mypy pplx_sdk --ignore-missing-imports

# Update stubs
pip install types-requests types-setuptools
```

### Import Errors

```bash
# Reinstall package in editable mode
uv pip install -e .

# Clear cache
rm -rf pplx_sdk/__pycache__
rm -rf .pytest_cache
```

### SSE Parsing Issues

- Verify line-by-line parsing
- Handle `:` comments (skip)
- Handle empty lines (skip)
- Stop on `[end]` marker
- Don't skip `event:` lines, use for metadata

## Documentation

### Docstring Template

```python
def method(
    self,
    param1: str,
    param2: Optional[int] = None,
) -> Dict[str, Any]:
    """One-line summary.

    Longer description if needed. Explain the behavior,
    use cases, and important details.

    Args:
        param1: Description.
        param2: Optional description.

    Returns:
        Description of return value.

    Raises:
        ValueError: When X happens.
        TimeoutError: When timeout exceeded.

    Example:
        >>> method("test")
        {...}
    """
    ...
```

### Update README

If adding new features, update README.md examples:

```bash
# Usage
git diff README.md
```

## Performance

- Avoid blocking I/O in generators
- Use httpx streaming for large responses
- Cache authentication headers
- Profile with cProfile if needed

## Security

- Never log session tokens
- Validate input types (Pydantic)
- Use HTTPS for API calls
- Handle 401/403 gracefully
- Don't commit .env files

## Release Process

Maintainers only:

```bash
# Update version in pplx_sdk/__init__.py
__version__ = "0.2.0"

# Update CHANGELOG.md

# Create tag
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin v0.2.0

# Build and publish
python -m build
twine upload dist/*
```

## Questions?

- Open an [issue](https://github.com/pv-udpv/pplx-sdk/issues)
- Check [README](README.md) first
- See `.copilot-instructions.md` for code standards

---

Thank you for contributing! 🚀
