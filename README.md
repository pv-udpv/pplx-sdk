# pplx-sdk

**Python SDK for Perplexity AI** with REST API wrappers and OpenAI-compatible API layer.

> Expose Perplexity AI as an OpenAI-compatible endpoint that works with any OpenAI client library.

## Features

- **🔌 SDK Wrappers** - Type-safe, Pydantic models for all Perplexity AI entities
- **🚀 Async/Sync** - Both synchronous and asynchronous clients
- **🔄 Streaming** - Full support for streaming responses
- **🌐 OpenAI Compatible** - Drop-in replacement layer for OpenAI API
- **📡 FastAPI Server** - Production-ready FastAPI server exposing OpenAI-compatible endpoints
- **🔍 Reverse-Engineered** - Based on deep analysis of Perplexity AI web client
- **🐍 Python 3.12+** - Modern Python with full type hints

## Installation

```bash
# Clone and install
git clone https://github.com/pv-udpv/pplx-sdk.git
cd pplx-sdk

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .[dev]

# Or with pip
pip install -e .[dev]
```

## Quick Start

### Basic Usage

```python
import os
from pplx_sdk import AsyncPplxClient, ChatCompletionMessage, ChatCompletionRole

# Set your API key
os.environ["PPLX_API_KEY"] = "your-api-key"

async def main():
    async with AsyncPplxClient() as client:
        response = await client.chat_complete(
            messages=[
                ChatCompletionMessage(
                    role=ChatCompletionRole.USER,
                    content="What is the capital of France?"
                )
            ]
        )
        print(response)

# Run with asyncio
import asyncio
asyncio.run(main())
```

### Streaming

```python
async def stream_example():
    async with AsyncPplxClient() as client:
        stream = await client.chat_complete(
            messages=[
                ChatCompletionMessage(
                    role=ChatCompletionRole.USER,
                    content="Explain quantum computing"
                )
            ],
            stream=True
        )
        async for chunk in stream:
            print(chunk.choices[0].delta.content, end="")
```

### OpenAI Compatible API

```python
from openai import AsyncOpenAI

# Point OpenAI client to your pplx-sdk server
client = AsyncOpenAI(
    api_key="your-pplx-api-key",
    base_url="http://localhost:8000/v1"
)

# Use exactly like OpenAI API
response = await client.chat.completions.create(
    model="llama-3.1-sonar-large-128k-online",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

## Architecture

```
pplx-sdk/
├── src/pplx_sdk/
│   ├── __init__.py           # Public API exports
│   ├── config.py             # Configuration (Pydantic Settings)
│   ├── models.py             # Pydantic data models
│   ├── client.py             # Sync/Async clients
│   ├── openai_compat.py      # OpenAI compatibility layer
│   └── fastapi_server.py     # Production FastAPI server
├── tests/                    # Test suite
├── docs/                     # Documentation
├── pyproject.toml            # Project metadata & dependencies
└── README.md                 # This file
```

## Configuration

Environment variables:

```bash
PPLX_API_KEY=your-api-key                              # Required
PPLX_API_BASE=https://api.perplexity.ai                # Optional
PPLX_API_TIMEOUT=60                                    # Request timeout (seconds)
PPLX_DEFAULT_MODEL=llama-3.1-sonar-large-128k-online   # Default model
PPLX_STREAM_MODE=sse                                   # Stream mode (rest/sse)
PPLX_TEMPERATURE=0.7                                   # Default temperature
```

## Running the FastAPI Server

```bash
# Install with FastAPI dependencies
uv pip install -e ".[dev,fastapi]"

# Run server
uvicorn pplx_sdk.fastapi_server:app --reload --port 8000

# Test health check
curl http://localhost:8000/health

# Test chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-sonar-large-128k-online",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Development

### Setup Development Environment

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v --cov=src/pplx_sdk
```

### Code Quality

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Project Status

🚀 **Alpha** - Core functionality implemented. API may change.

## Roadmap

- [ ] Full entity wrappers (threads, spaces, connectors, etc.)
- [ ] Advanced streaming with event callbacks
- [ ] Caching layer
- [ ] Rate limiting
- [ ] Comprehensive test suite
- [ ] Production deployment guide
- [ ] Documentation site

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create feature branch (`git checkout -b feature/thing`)
3. Add tests
4. Run linting/typing
5. Submit PR

## License

MIT

## References

- [Perplexity AI](https://www.perplexity.ai)
- [OpenAI API](https://openai.com/api/)
- [Reverse-engineered API Docs](https://github.com/pv-udpv/perplexity-ai-unofficial)
