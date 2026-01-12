# Contributing to pplx-sdk

Thank you for your interest in contributing to the Perplexity Python SDK!

## Development Setup

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pv-udpv/pplx-sdk.git
cd pplx-sdk
```

2. Create a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
# Install package in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Or install with API server support
uv pip install -e ".[dev,api]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pplx_sdk --cov-report=html

# Run specific test file
pytest tests/test_transport.py

# Run specific test
pytest tests/test_transport.py::test_http_transport
```

### Code Quality

We use several tools to maintain code quality:

#### Linting

```bash
# Run ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

#### Formatting

```bash
# Format with black
black pplx_sdk tests

# Check formatting
black --check pplx_sdk tests

# Or use ruff formatter
ruff format .
```

#### Type Checking

```bash
# Run mypy type checker
mypy pplx_sdk

# Check specific file
mypy pplx_sdk/client.py
```

#### Import Sorting

```bash
# Sort imports with isort
isort pplx_sdk tests

# Check import order
isort --check-only pplx_sdk tests
```

### Running the API Server

```bash
# Set authentication token
export PPLX_AUTH_TOKEN="your-session-token"

# Run server
uvicorn pplx_sdk.api.oai_server:app --reload --port 8000

# Or use Python directly
python -m pplx_sdk.api.oai_server
```

## Coding Standards

### Style Guide

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings in Google style format
- Maximum line length: 100 characters

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description if needed, explaining behavior and usage.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
        TypeError: Description of when this is raised

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Type Hints

Always include type hints:

```python
from typing import Optional, List, Dict, Any

def process_data(
    items: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, int]:
    """Process data and return results."""
    pass
```

## Testing Guidelines

### Test Structure

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names

Example:

```python
def test_http_transport_request():
    """Test HTTP transport makes requests correctly."""
    transport = HttpTransport(auth_token="test-token")
    # Test implementation
```

### Test Coverage

- Aim for >80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions

### Mock External Dependencies

Use `pytest-httpx` to mock HTTP requests:

```python
import pytest
import httpx
from pytest_httpx import HTTPXMock

def test_api_call(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.example.com/endpoint",
        json={"status": "success"}
    )
    # Test implementation
```

## Pull Request Process

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for new functionality

4. **Run quality checks**:
   ```bash
   ruff check --fix .
   black pplx_sdk tests
   mypy pplx_sdk
   pytest --cov=pplx_sdk
   ```

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add new feature description"
   ```

   Use conventional commit format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to related issues
   - Test results
   - Screenshots (if applicable)

## Project Structure

```
pplx-sdk/
├── pplx_sdk/              # Main package
│   ├── __init__.py        # Public API exports
│   ├── client.py          # Main client and Conversation API
│   ├── domain/            # Domain models and services
│   │   ├── models.py      # Pydantic models
│   │   ├── entries.py     # Entries service
│   │   └── ...
│   ├── transport/         # HTTP and SSE transport
│   │   ├── http.py        # HTTP client wrapper
│   │   └── sse.py         # SSE streaming
│   ├── streaming/         # Streaming utilities
│   │   ├── manager.py     # Retry and reconnection
│   │   └── ...
│   ├── api/               # OpenAI-compatible API
│   │   ├── oai_server.py  # FastAPI server
│   │   └── ...
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── examples/              # Example scripts
└── docs/                  # Documentation
```

## Documentation

### Adding Documentation

- Update docstrings for all public APIs
- Add examples to docstrings
- Update README.md for user-facing changes

### Building Documentation

```bash
# Install docs dependencies
uv pip install -e ".[docs]"

# Build docs with Sphinx
cd docs
make html

# View docs
open _build/html/index.html
```

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Join our community chat (link TBD)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
