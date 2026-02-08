# pplx-sdk: Perplexity AI Python SDK

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-grade Python SDK for Perplexity AI with:
- **Native SSE streaming** via `/rest/sse/perplexity_ask`
- **OpenAI-compatible API** wrapper (`/v1/chat/completions` format)
- **Full entity wrappers**: `Conversation` bound => Chat (oai chats), Thread(oai agents, ask/search), Entry -> Message, Collections -> Spaces, Articles -> Pages 
- **Reconnection & retry logic** with backoff
- **Type-safe** with Pydantic v2 models
- **Async-first** architecture

## Quick Start

### Installation

```bash
uv venv
uv pip install -e .
```

### Basic Usage (Native API)

```python
from pplx_sdk import PerplexityClient, Conversation

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<pplx-session-token>"  # from browser cookies
)

# Create conversation
conv = client.new_conversation(title="Research")

# Stream response
for chunk in conv.ask_stream("Explain quantum computing", mode="research"):
    print(chunk.text, end="", flush=True)

# Get full entry
entry = conv.ask("What are its applications?")
print(f"\nFinal response: {entry.text_completed}")
```

### OpenAI-Compatible API (HTTP)

Run the adapter server:

```bash
uvicorn pplx_sdk.api.oai_server:app --host 0.0.0.0 --port 8000
```

Use like OpenAI:

```python
from openai import OpenAI

client = OpenAI(
    api_key="unused",  # pplx uses session auth
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="pplx-70b-chat",
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Architecture

### Low-Level: SSE Transport

Direct SSE streaming from `/rest/sse/perplexity.ask`:

```python
from pplx_sdk.transport import SSETransport

transport = SSETransport(
    client=httpx_client,
    endpoint="https://www.perplexity.ai/rest/sse/perplexity.ask"
)

for chunk in transport.stream(
    query="What is machine learning?",
    context_uuid="<uuid>",
    mode="concise",
    model_preference="pplx-70b-chat"
):
    print(f"Status: {chunk.status}, Data: {chunk.data}")
```

**Stream Events**:
- `query_progress` → search status
- `search_results` → web results
- `answer_started` → generation begins
- `answer_chunk` → token (streaming)
- `final_response` → complete JSON response
- `related_questions` → follow-ups
- `error` → failure with retry hint

### Mid-Level: Domain Services

```python
client.threads.get(slug_or_uuid)
client.entries.stream_ask(query, context_uuid, mode="research")
client.entries.ask(query, ...)  # returns full Entry
client.collections.save_thread_to_collection(thread, collection_id)
client.articles.from_thread(thread)  # convert to article
```

### High-Level: Conversation API

```python
# Stateful conversation with UX-friendly interface
conv = client.new_conversation(title="Research")

# Build on previous messages
for msg in conv.ask_stream("Explain X", mode="research"):
    print(msg.text, end="")

entry = conv.ask("Now compare with Y")

# Fork at any point
forked = conv.fork(from_entry=entry)
forked.ask("Continue differently...")

# Save to collection
conv.save_to_collection(collection_id)
conv.to_article()  # Convert thread to article
```

## Core Data Models

### Pydantic Schemas

**Thread** (via `domain.models`):
```python
@dataclass
class Thread:
    context_uuid: str  # primary key
    title: Optional[str]
    slug: str
    access: Literal["private", "org", "public"]
    fork_count: int
    like_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
```

**Entry**:
```python
@dataclass
class Entry:
    backend_uuid: str  # primary key
    frontend_uuid: str  # client-generated
    context_uuid: str  # parent thread
    status: Literal["pending", "completed", "failed", "resuming"]
    text_completed: bool
    blocks: List[Block]  # structured answer
    sources: List[Source]
```

**MessageChunk** (SSE event):
```python
@dataclass
class MessageChunk:
    type: str  # query_progress, answer_chunk, final_response, etc.
    status: Optional[str]
    data: Dict[str, Any]  # event-specific payload
    backend_uuid: str
    context_uuid: str
```

## Authentication

### Session-Based (Browser Tokens)

```python
client = PerplexityClient(
    auth_token="<pplx.session-id>"  # from cookies
)
```

**Get token**:
1. Open perplexity.ai in browser
2. DevTools → Application → Cookies
3. Find `pplx.session-id` or `pplx_session`

### Headers Included

- `Authorization: Bearer <session-token>`
- `X-Client-Name: web`
- `X-App-Version: <current>`
- `X-Device-ID: <uuid>`
- `Accept: text/event-stream`
- `Content-Type: application/json`

## SSE Request/Response Reference

### POST `/rest/sse/perplexity.ask`

**Request Body**:
```json
{
  "query_str": "Explain quantum computing",
  "context_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "frontend_uuid": "550e8400-e29b-41d4-a716-446655440001",
  "mode": "research",
  "model_preference": "pplx-70b-chat",
  "search_focus": "internet",
  "sources": ["web"],
  "language": "en-US",
  "timezone": "Europe/Moscow",
  "is_incognito": false,
  "parent_entry_uuid": null,
  "existing_entry_uuids": [],
  "resume_entry_uuids": [],
  "cursor": null,
  "use_schematized_api": true
}
```

**Response Stream** (text/event-stream):
```
event: query_progress
data: {"status": "search_started", "steps": "INITIALIZING"}

event: search_results
data: {"results": [{"url": "...", "title": "..."}]}

event: answer_started
data: {}

event: answer_chunk
data: {"text": "Quantum computing is..."}

event: answer_chunk
data: {"text": " a field that..."}

event: final_response
data: {"backend_uuid": "...", "display_model": "pplx-70b-chat", ...}

: \[end]
```

## Streaming & Reconnection

### Automatic Reconnection

```python
from pplx_sdk.streaming import StreamManager

manager = StreamManager(
    max_retries=3,
    retry_backoff_ms=1500,
    timeout_ms=30000
)

for chunk in manager.stream(
    query="...",
    context_uuid="...",
    reconnectable=True  # resume on disconnect
):
    if chunk.type == "error":
        print(f"Error (will retry): {chunk.data}")
```

**Resume Logic**:
1. Stream disconnects midway
2. Server returns `cursor` in final chunk
3. Client sends `resume_entry_uuids` + `cursor` to resume
4. Server re-streams from checkpoint

## OpenAI Compatibility Layer

### Adapter Server

Run on port 8000:

```bash
PPLX_AUTH_TOKEN=<token> uvicorn pplx_sdk.api.oai_server:app
```

**Endpoints**:
- `POST /v1/chat/completions` → SSE streaming
- `POST /v1/models` → list available models
- `GET /v1/health` → health check

**Model Mapping**:
- `gpt-4-turbo` → `pplx-70b-deep` (research mode)
- `gpt-3.5-turbo` → `pplx-7b-online` (fast mode)
- `pplx-70b-chat` → default

**Usage with OpenAI Client**:

```python
from openai import OpenAI
import httpx

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="unused"
)

# Standard OpenAI call
response = client.chat.completions.create(
    model="pplx-70b-chat",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    stream=True,
    temperature=0.7,
    max_tokens=2048
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Project Structure

```
pplx-sdk/
├── README.md                          # This file
├── pyproject.toml                     # uv config, dependencies
├── pplx_sdk/
│   ├── __init__.py                    # Public API
│   ├── client.py                      # PerplexityClient root
│   ├── transport/
│   │   ├── http.py                    # HttpTransport (httpx wrapper)
│   │   ├── sse.py                     # SSETransport (streaming)
│   │   └── base.py                    # Transport protocol
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py                  # Pydantic schemas
│   │   ├── threads.py                 # ThreadsService
│   │   ├── entries.py                 # EntriesService (core Ask API)
│   │   ├── memories.py                # MemoriesService
│   │   ├── collections.py             # CollectionsService
│   │   └── articles.py                # ArticlesService
│   ├── streaming/
│   │   ├── manager.py                 # StreamManager (retry/reconnect)
│   │   ├── parser.py                  # SSE event parser
│   │   └── types.py                   # Event type definitions
│   ├── api/
│   │   ├── __init__.py
│   │   ├── oai_server.py              # FastAPI OpenAI adapter
│   │   ├── oai_models.py              # OpenAI Pydantic models
│   │   └── middleware.py              # Auth, logging
│   └── utils/
│       ├── auth.py                    # Token extraction helpers
│       └── logging.py                 # Structured logging
├── tests/
│   ├── test_transport.py              # Transport layer tests
│   ├── test_streaming.py              # Streaming/retry tests
│   ├── test_oai_compat.py             # OpenAI adapter tests
│   └── fixtures/                      # Mock SSE responses
└── examples/
    ├── basic_conversation.py          # Conversation API demo
    ├── sse_streaming.py               # Low-level SSE demo
    ├── oai_compatible.py              # OpenAI client demo
    └── advanced_retry.py              # Custom retry logic
```

## Agent & Subagent Architecture

> 📚 **[Comprehensive Research & Documentation](./docs/README.md)** — See `docs/` for detailed analysis of the agentic system, including:
> - Latest merged PR #22 analysis
> - Dual-path architecture (Copilot + external runners)
> - Agent handoff workflows with real issue tests
> - Visual architecture diagrams
> - Test scripts and scenarios

pplx-sdk includes a multi-agent development system with specialist subagents coordinated by an orchestrator. There are **three ways** to use it depending on your environment.

### Architecture Overview

```
┌──────────────────────────────┐
│  GitHub Copilot Coding Agent │  ← prompt + MCP only
│  .github/copilot-            │     (no agent.json, no tasks)
│    instructions.md           │
│  .copilot/mcp.json           │
└──────────────┬───────────────┘
               │ (capabilities via MCP)
               ▼
┌──────────────────────────────┐
│     MCP Servers              │  ← shared capability layer
│  (fetch, context7,           │
│   deepwiki, llms-txt)        │
└──────────────┬───────────────┘
               │ (also used by)
               ▼
┌──────────────────────────────┐
│  External runners            │  ← agent.json + tasks + skills
│  (Cline, obra/superpowers)   │
│  tasks/*.json                │
│  skills/*/SKILL.md           │
│  .claude/agents/*.md         │
│  agent.json                  │
└──────────────────────────────┘
```

### Available Subagents

Each subagent is defined in `.claude/agents/` with restricted tool access and isolated context:

| Subagent | File | Capabilities |
|----------|------|-------------|
| `orchestrator` | `.claude/agents/orchestrator.md` | Decomposes tasks, coordinates other subagents |
| `code-reviewer` | `.claude/agents/code-reviewer.md` | Read-only code review, architecture compliance |
| `test-runner` | `.claude/agents/test-runner.md` | Run/fix tests, coverage analysis |
| `scaffolder` | `.claude/agents/scaffolder.md` | Create new modules, files, exports |
| `sse-expert` | `.claude/agents/sse-expert.md` | SSE streaming, parsing, reconnection |
| `reverse-engineer` | `.claude/agents/reverse-engineer.md` | API discovery, traffic analysis, schema decoding |
| `architect` | `.claude/agents/architect.md` | Architecture diagrams, design validation |
| `spa-expert` | `.claude/agents/spa-expert.md` | SPA reverse engineering (React/Vite/Workbox/CDP) |
| `codegraph` | `.claude/agents/codegraph.md` | AST parsing, dependency graphs, knowledge graphs |
| `awesome-copilot` | `.claude/agents/awesome-copilot.md` | Manage pplx-sdk collection for github/awesome-copilot |

### Running Subagents

#### Option 1: GitHub Copilot Coding Agent

GitHub Copilot reads the prompt (`.github/copilot-instructions.md`) and MCP config (`.copilot/mcp.json`) — it does **not** load `agent.json`, tasks, or skills from disk. Skill behaviors are embedded directly in the prompt.

To use skills with Copilot, just describe what you need. The embedded behaviors guide it automatically:

```
# In a GitHub Copilot session:
"Review pplx_sdk/transport/http.py for architecture compliance"
→ Copilot uses embedded code-review behavior

"Fix the failing test in tests/test_transport.py"
→ Copilot uses embedded test-fix behavior

"Create a new CacheService in the domain layer"
→ Copilot uses embedded scaffold-module behavior
```

#### Option 2: External Agent Runners (Cline, obra/superpowers, custom)

External runners load `agent.json` and execute task templates from `tasks/*.json`. Each task wraps a skill into an executable action:

```python
import json

# Load a task template
with open("tasks/code-review.json") as f:
    task = json.load(f)

# Fill in dynamic inputs
task["inputs"]["target"] = "pplx_sdk/transport/http.py"

# Execute via your runner
runner.execute(task)
```

Available task templates:

| Task | Skill | Agent Type | Purpose |
|------|-------|------------|---------|
| `tasks/code-review.json` | code-review | review | Review code against architecture conventions |
| `tasks/test-fix.json` | test-fix | test | Diagnose and fix failing tests |
| `tasks/scaffold-module.json` | scaffold-module | implement | Create new modules per layered architecture |
| `tasks/sse-streaming.json` | sse-streaming | implement | Implement SSE streaming features |
| `tasks/reverse-engineer.json` | reverse-engineer | explore | Discover undocumented API endpoints |
| `tasks/architecture.json` | architecture | analyze | Generate architecture diagrams |
| `tasks/code-analysis.json` | code-analysis | analyze | AST parsing and dependency analysis |
| `tasks/explore.json` | pplx-sdk-dev | explore | General codebase exploration |
| `tasks/full-workflow.json` | pplx-sdk-dev | orchestrate | End-to-end feature workflow |

#### Option 3: Claude Code with Subagent Delegation

When using Claude Code with the `.claude/agents/` directory, the orchestrator coordinates specialist subagents through workflow phases:

```
[plan] → [explore] → [research] → [implement] → [test] → [review] → [done]
```

Skills use `context: fork` for isolated execution. The meta-skill `pplx-sdk-dev` (in `skills/pplx-sdk-dev/SKILL.md`) activates the orchestrator, which delegates to specialists:

```yaml
# skills/pplx-sdk-dev/SKILL.md frontmatter
---
name: pplx-sdk-dev
description: Meta-skill that orchestrates all development workflows
context: fork
agent: orchestrator
---
```

The orchestrator follows predefined workflows based on the task type:

| Workflow | Phases | When to Use |
|----------|--------|-------------|
| `new-feature` | plan → explore → research → scaffold → implement → test → review → verify | Building new SDK features |
| `bug-fix` | reproduce → research → diagnose → fix → verify | Fixing bugs |
| `sse-streaming` | research → implement → test → review | SSE/streaming work |
| `api-discovery` | capture → research → document → scaffold → implement → test → review | Reverse engineering endpoints |
| `architecture` | analyze → research → diagram → validate → document | Architecture diagrams |
| `code-analysis` | parse → graph → analyze → report → act | Code quality analysis |

### Skills Directory

Skills are defined in `.agents/skills/` and symlinked into `skills/` for convenience. Each contains a `SKILL.md` with YAML frontmatter. Subagent definitions (`.md` files) live separately in `.claude/agents/`.

```
skills/
├── code-review/SKILL.md       # Architecture compliance review
├── test-fix/SKILL.md          # Diagnose and fix test failures
├── scaffold-module/SKILL.md   # Create new layered modules
├── sse-streaming/SKILL.md     # SSE implementation patterns
├── reverse-engineer/SKILL.md  # API discovery from traffic
├── architecture/SKILL.md      # Mermaid diagrams
├── code-analysis/SKILL.md     # AST parsing and graphs
├── spa-reverse-engineer/SKILL.md  # SPA internals via CDP
└── pplx-sdk-dev/SKILL.md     # Meta-skill (orchestrator)
```

### Awesome Copilot Collection

The `awesome-copilot/` directory contains a collection ready for submission to [github/awesome-copilot](https://github.com/github/awesome-copilot) — the community hub for GitHub Copilot customizations.

```
awesome-copilot/
├── instructions/pplx-sdk-python.instructions.md  # Coding conventions
├── agents/pplx-sdk-expert.agent.md                # Expert chat mode
├── prompts/pplx-sdk-scaffold.prompt.md            # Module scaffolding prompt
└── collections/pplx-sdk-development.collection.yml # Collection manifest
```

The `awesome-copilot` subagent (`.claude/agents/awesome-copilot.md`) manages this collection — validating items, syncing with upstream, and preparing PRs.

### MCP Servers

All agent environments share MCP servers defined in `.copilot/mcp.json`:

| Server | Type | Purpose |
|--------|------|---------|
| `github-rw` | HTTP (`api.githubcopilot.com`) | GitHub read-write operations via MCP |
| `perplexity_ai` | HTTP (`api.perplexity.ai`) | Perplexity AI search and reasoning |
| `deep-wiki` | `mcp-deepwiki` | GitHub repo documentation search |
| `fetch` | `@anthropic-ai/mcp-fetch` | Fetch any URL as markdown |
| `context7` | `@upstash/context7-mcp` | Context-aware library docs |
| `llms-txt` | `@mcp-get-community/server-llm-txt` | LLM-optimized docs via llms.txt |

## Development

### Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (creates venv automatically)
uv sync --all-extras --dev

# Run tests
uv run pytest -v

# Type check
uv run mypy pplx_sdk

# Format
uv run ruff format .
uv run ruff check --fix .
```

### Dependencies

**Core**:
- `httpx>=0.25.0` → HTTP client with streaming
- `pydantic>=2.0` → Data validation
- `python-dotenv` → Config from .env

**Dev**:
- `pytest>=7.0` → Testing
- `pytest-asyncio` → Async test support
- `pytest-httpx` → Mock HTTP responses
- `mypy>=1.0` → Type checking
- `ruff` → Linting/formatting
- `black` → Code formatting

**API Server**:
- `fastapi>=0.100` → API framework
- `uvicorn>=0.23` → ASGI server

## API Reference

### PerplexityClient

```python
class PerplexityClient:
    def __init__(
        self,
        api_base: str = "https://www.perplexity.ai",
        auth_token: str = None,  # pplx.session-id from cookies
        timeout: float = 30.0,
        default_headers: Optional[Dict[str, str]] = None
    )
    
    # High-level conversation API
    def new_conversation(self, title: Optional[str] = None) -> Conversation
    def conversation_from_thread(self, slug_or_uuid: str) -> Conversation
    
    # Low-level domain services
    @property
    def threads(self) -> ThreadsService
    @property
    def entries(self) -> EntriesService
    @property
    def memories(self) -> MemoriesService
    @property
    def collections(self) -> CollectionsService
    @property
    def articles(self) -> ArticlesService
```

### Conversation

```python
class Conversation:
    context_uuid: str
    thread: Thread
    entries: List[Entry]
    
    async def ask_stream(
        self,
        query: str,
        mode: Optional[str] = None,
        model_preference: Optional[str] = None,
        sources: Optional[Dict[str, Any]] = None
    ) -> Generator[MessageChunk]
    
    async def ask(
        self,
        query: str,
        **kwargs
    ) -> Entry
    
    def fork(self, from_entry: Optional[Entry] = None) -> Conversation
    
    def save_to_collection(self, collection_id: str) -> None
    
    def to_article(self) -> Article
```

## Troubleshooting

### 401 Unauthorized

**Cause**: Session token expired or invalid

**Fix**: Refresh token from browser cookies:
```python
client = PerplexityClient(auth_token="<new-token>")
```

### 429 Rate Limited

**Cause**: Too many requests

**Fix**: Use backoff with StreamManager:
```python
manager = StreamManager(retry_backoff_ms=2000, max_retries=5)
```

### SSE Timeout After 30s

**Cause**: Research mode queries may take >30s

**Fix**: Increase timeout:
```python
streammanager = StreamManager(timeout_ms=60000)
```

## License

MIT

## Contributing

Fork → Feature branch → Tests → PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
