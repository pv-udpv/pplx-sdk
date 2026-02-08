# Architecture Overview

> This document synthesizes architectural patterns from @pv-udpv/perplexity-ai-unofficial and @pv-udpv/pplx-unofficial-sdk

## Layered Architecture

### Current pplx-sdk Architecture

```
pplx-sdk/
├── core/                  # Protocols, types, exceptions (lowest layer)
│   ├── protocols.py      # Transport, SSE protocols
│   ├── types.py          # Type aliases, shared types
│   └── exceptions.py     # Custom exception hierarchy
├── shared/               # Reusable utilities
│   └── retry.py         # Retry logic with backoff
├── utils/                # Shared utilities
│   ├── auth.py          # Authentication utilities
│   └── logging.py       # Logging configuration
├── transport/           # HTTP/SSE backends
│   ├── http.py          # HTTP transport
│   └── sse.py           # SSE transport
├── domain/              # Business logic
│   ├── threads.py       # Thread management (stub)
│   ├── entries.py       # Entry/message management
│   ├── collections.py   # Collections/spaces (stub)
│   ├── articles.py      # Articles service (stub)
│   └── memories.py      # Memories service (stub)
├── streaming/           # SSE streaming engine
│   ├── manager.py       # Stream manager
│   ├── parser.py        # SSE parser
│   └── types.py         # Streaming types
└── client.py           # High-level API (PerplexityClient, Conversation)
```

### Inspiration from pplx-unofficial-sdk

The TypeScript SDK uses a similar modular architecture with clear separation:

```
@pplx-unofficial/sdk
├── stream/              # SSE streaming layer
│   └── pplx-client.ts  # Real-time streaming engine
├── rest/                # REST API layer
│   └── pplx-rest-client.ts  # CRUD operations
├── connectors/          # OAuth integration layer
│   └── pplx-connectors-client.ts  # 9+ service integrations
└── service-worker/      # Service worker analysis
    └── sw-client.ts    # Asset tracking & versioning
```

## Key Architectural Principles

### 1. Protocol-Oriented Design

Both repositories use **protocol/interface-first design**:

- **Python**: `Protocol` classes from `typing` module
- **TypeScript**: Interfaces and type definitions

This enables:
- Loose coupling between layers
- Easy mocking for tests
- Multiple transport implementations

### 2. Async-First Architecture

All I/O operations are asynchronous:
- Python: `async`/`await` with `asyncio`
- TypeScript: Promises and async generators

Benefits:
- Non-blocking I/O for streaming
- Efficient resource utilization
- Better concurrency handling

### 3. Streaming-First API Design

Both SDKs prioritize streaming over request-response:

**Python (current)**:
```python
for chunk in conv.ask_stream("query"):
    print(chunk.text, end="")
```

**TypeScript (unofficial SDK)**:
```typescript
for await (const entry of sdk.stream.search("query")) {
    console.log(entry.status);
    if (entry.final) console.log(entry.blocks);
}
```

### 4. Layered Dependency Flow

```
┌─────────────────────────────────────┐
│         Client/Application          │  High-level API
├─────────────────────────────────────┤
│      Domain/Business Logic          │  Threads, Entries, Collections
├─────────────────────────────────────┤
│    Transport/Streaming Layer        │  HTTP, SSE, WebSocket
├─────────────────────────────────────┤
│         Shared Utilities            │  Retry, Auth, Logging
├─────────────────────────────────────┤
│      Core (Protocols & Types)       │  Base abstractions
└─────────────────────────────────────┘
```

**Rules**:
- Lower layers never import from higher layers
- Each layer depends only on layers below it
- Core has zero dependencies on other layers

## Protocol Support

### Perplexity API Protocol 2.17-2.18

The unofficial SDK tracks protocol versions from Perplexity's web app:

**Current Protocol**: 2.18
**Total Endpoints**: 38+
- 2 SSE streaming endpoints
- 24 REST API endpoints
- 11 OAuth connector endpoints
- 1 Service worker endpoint

### SSE Streaming Protocol

**Endpoint**: `/rest/sse/perplexity.ask`

**Event Types**:
1. `query_progress` - Search status updates
2. `search_results` - Web search results
3. `answer_chunk` - Incremental AI response tokens
4. `final_response` - Complete response with metadata
5. `error` - Error information

**Protocol Features**:
- Cursor-based resumption for reconnection
- JSON Patch (RFC-6902) for differential updates
- Rate limit headers in responses
- CSRF protection via state parameters

## Microservices Architecture (from pplx-unofficial-sdk)

The TypeScript project evolved into a microservices architecture:

```
┌──────────────────────────────────────────────────────────┐
│                    API Gateway (8000)                     │
│         Rate limiting, CORS, routing, auth injection      │
└────────────┬─────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬────────────────┐
    │                 │              │                │
┌───▼────┐    ┌──────▼─────┐  ┌────▼──────┐  ┌─────▼──────┐
│  Auth  │    │ Knowledge  │  │ Analysis  │  │   Asset    │
│ Service│    │    API     │  │  Service  │  │  Fetcher   │
│ (8001) │    │  (8002)    │  │  (8003)   │  │  (8004)    │
└────────┘    └────────────┘  └───────────┘  └────────────┘
```

### Service Responsibilities

1. **API Gateway (Port 8000)**
   - Request routing
   - Rate limiting and CORS
   - Authentication token injection
   - Health checks and monitoring

2. **Auth Service (Port 8001)**
   - NextAuth flow implementation
   - Session pool management
   - Token rotation and refresh
   - Multi-account support

3. **Knowledge API (Port 8002)**
   - SSE streaming endpoints
   - REST CRUD operations
   - Database integration
   - Cache layer for performance

4. **Analysis Service (Port 8003)**
   - Tree-sitter AST parsing
   - Dependency graph generation
   - ML pipeline integration
   - Traffic pattern analysis

5. **Asset Fetcher (Port 8004)**
   - Service worker parsing
   - Asset mirroring and updates
   - Version tracking
   - Incremental synchronization

## Design Patterns

### 1. Factory Pattern

Both SDKs use factories for client creation:

**Python**:
```python
client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)
```

**TypeScript**:
```typescript
const sdk = createPplxSDK();
const stream = createPplxClient();
const rest = createRestClient();
```

### 2. Builder Pattern

Conversation/thread creation uses builder-like patterns:

**Python**:
```python
conv = client.new_conversation(
    title="Research",
    mode="research",
    model="pplx-70b-chat"
)
```

### 3. Iterator Pattern

Streaming uses async iterators:

**Python**:
```python
for chunk in transport.stream(query="...", context_uuid="..."):
    print(chunk.status, chunk.data)
```

**TypeScript**:
```typescript
for await (const entry of sdk.stream.search("query")) {
    // Process entry
}
```

### 4. Strategy Pattern

Multiple transport implementations:

**Python**:
- `HttpxTransport` - Standard httpx backend
- `CurlCffiTransport` - curl_cffi for advanced features

**TypeScript**:
- Native fetch API
- Node.js http module
- Configurable HTTP clients

## Error Handling Architecture

### Custom Exception Hierarchy

**Python (current)**:
```python
PerplexityError
├── TransportError
│   ├── HTTPError
│   └── SSEError
├── AuthenticationError
├── ValidationError
└── RateLimitError
```

### Retry Strategy

Both SDKs implement exponential backoff with jitter:

**Configuration**:
- Initial backoff: 1000ms
- Max retries: 3-5
- Max backoff: 30000ms
- Jitter: 0-25%

**Retryable Conditions**:
- Network errors (connection timeout, DNS failure)
- HTTP 5xx errors (server errors)
- HTTP 429 (rate limit)
- SSE reconnection (with cursor)

## Comparison: Python vs TypeScript SDK

| Feature | pplx-sdk (Python) | pplx-unofficial-sdk (TypeScript) |
|---------|-------------------|----------------------------------|
| **Language** | Python 3.12+ | TypeScript 5.3+ |
| **Async Model** | asyncio | Promises/async-await |
| **Type System** | mypy strict mode | TypeScript strict |
| **Streaming** | SSE via httpx | SSE via fetch/EventSource |
| **REST API** | Full CRUD | Full CRUD + extended |
| **OAuth** | Not yet implemented | 9+ connectors |
| **Service Worker** | Not yet implemented | Full analysis tools |
| **Microservices** | Monolithic SDK | Microservices architecture |
| **Protocol Version** | 2.17 | 2.18 |
| **Bundle Size** | N/A (Python) | Tree-shakeable |
| **Pagination** | Standard iteration | AsyncGenerator |

## Future Architecture Considerations

### From pplx-unofficial-sdk Learnings

1. **OAuth Connector Layer**
   - Add `pplx_sdk/connectors/` module
   - Support Google Drive, Notion, OneDrive, etc.
   - OAuth flow management
   - File import/sync capabilities

2. **Service Worker Analysis**
   - Add `pplx_sdk/analysis/` module
   - Track Perplexity app versions
   - Extract chunk manifests
   - Detect protocol changes

3. **Enhanced REST API**
   - Entry forking support
   - Collection management (Spaces)
   - JSON Patch support for updates
   - Advanced pagination with cursors

4. **Rate Limiting**
   - Built-in rate limiter
   - Per-endpoint rate limits
   - Automatic retry with backoff
   - Rate limit header parsing

5. **Multi-Account Support**
   - Session pool management
   - Token rotation
   - Account switching
   - Concurrent requests from multiple accounts

## References

- [pplx-unofficial-sdk GitHub](https://github.com/pv-udpv/pplx-unofficial-sdk)
- [Perplexity AI Official Docs](https://docs.perplexity.ai/)
- Protocol version: 2.17-2.18
- SSE Specification: [RFC 8895](https://www.rfc-editor.org/rfc/rfc8895.html)
- JSON Patch: [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html)
