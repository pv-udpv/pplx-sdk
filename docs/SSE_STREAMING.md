# SSE Streaming Protocol Guide

> Comprehensive guide to Server-Sent Events (SSE) streaming in Perplexity AI API, synthesized from @pv-udpv/pplx-unofficial-sdk research

## Overview

Perplexity AI uses Server-Sent Events (SSE) for real-time AI search responses. This protocol enables incremental delivery of search results, citations, and AI-generated content.

## SSE Protocol Basics

### What is SSE?

Server-Sent Events is a standard for server-to-client streaming over HTTP:

- **Unidirectional**: Server → Client only
- **Text-based**: UTF-8 encoded text stream
- **Event-driven**: Named events with associated data
- **Auto-reconnect**: Built-in reconnection with `Last-Event-ID`

### SSE Message Format

```
event: <event-type>
data: <json-payload>
id: <event-id>

```

**Key characteristics**:
- Each field on a separate line
- `data:` field can appear multiple times (concatenated with `\n`)
- Empty line (`\n\n`) marks end of event
- Lines starting with `:` are comments (ignored)

## Perplexity SSE Endpoint

### Primary Streaming Endpoint

```
POST https://www.perplexity.ai/rest/sse/perplexity.ask
Content-Type: application/json
Cookie: __Secure-next-auth.session-token=<token>
```

**Request Payload** (actual pplx-sdk implementation):
```json
{
  "query_str": "Explain quantum computing",
  "context_uuid": "<thread-uuid>",
  "frontend_uuid": "<entry-uuid>",
  "mode": "concise",
  "model_preference": "pplx-70b-chat",
  "sources": ["web"],
  "use_schematized_api": true,
  "language": "en-US",
  "timezone": "UTC",
  "is_incognito": false,
  "parent_entry_uuid": "<optional-parent-uuid>",
  "cursor": "<optional-resume-cursor>"
}
```

**Request Payload** (observed in pplx-unofficial-sdk web client):
```json
{
  "version": "2.18",
  "source": "default",
  "model": "pplx-70b-chat",
  "query": "Explain quantum computing",
  "context_uuid": "<thread-uuid>",
  "mode": "concise",
  "search_focus": "internet",
  "attachments": [],
  "language": "en-US"
}
```

> **Note**: The pplx-sdk uses a slightly different request schema than the web client. The web client uses `version`, `source`, `query`, and `search_focus`, while the SDK uses `query_str`, `frontend_uuid`, `model_preference`, `sources`, and `use_schematized_api`.

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Protocol version (e.g., "2.17", "2.18") |
| `source` | string | Yes | Request source ("default", "ios", "android") |
| `model` | string | Yes | Model ID (e.g., "pplx-70b-chat", "sonar-pro") |
| `query` | string | Yes | User query text |
| `context_uuid` | string | Yes | Thread/conversation UUID |
| `mode` | string | No | Response mode ("concise", "detailed") |
| `search_focus` | string | No | Search scope ("internet", "academic", "writing", "wolfram", "youtube", "reddit") |
| `attachments` | array | No | File attachments (from connectors) |
| `language` | string | No | Response language (default: "en-US") |

### Search Focus Options

1. **internet** (default) - General web search
2. **academic** - Scholarly articles and papers
3. **writing** - Creative writing mode
4. **wolfram** - Computational knowledge (Wolfram Alpha)
5. **youtube** - YouTube video search
6. **reddit** - Reddit discussions

## Event Types

### 1. `query_progress`

Search status updates:

```
event: query_progress
data: {"status": "searching", "message": "Searching the web..."}

event: query_progress
data: {"status": "processing", "message": "Analyzing results..."}
```

**Status values**:
- `searching` - Executing web search
- `processing` - Processing results
- `generating` - Generating response
- `completed` - Search completed

### 2. `search_results`

Web search results with citations:

```
event: search_results
data: {
data:   "results": [
data:     {
data:       "title": "Quantum Computing Explained",
data:       "url": "https://example.com/quantum",
data:       "snippet": "Quantum computers use quantum bits...",
data:       "favicon": "https://example.com/favicon.ico"
data:     }
data:   ]
data: }
```

**Result fields**:
- `title` - Page title
- `url` - Full URL
- `snippet` - Text excerpt
- `favicon` - Favicon URL (optional)
- `thumbnail` - Image thumbnail URL (optional)

### 3. `answer_chunk`

Incremental AI response tokens:

```
event: answer_chunk
data: {"text": "Quantum ", "index": 0}

event: answer_chunk
data: {"text": "computing ", "index": 1}

event: answer_chunk
data: {"text": "is a ", "index": 2}
```

**Chunk fields**:
- `text` - Token/word fragment
- `index` - Chunk sequence number
- `delta` - Text delta (for JSON Patch mode)

### 4. `final_response`

Complete response with all metadata:

```
event: final_response
data: {
data:   "uuid": "<entry-uuid>",
data:   "text_completed": "Quantum computing is...",
data:   "blocks": [
data:     {"type": "text", "content": "Quantum computing is..."}
data:   ],
data:   "sources_list": [
data:     {
data:       "title": "...",
data:       "url": "...",
data:       "citation_index": 1
data:     }
data:   ],
data:   "created_at": "2024-01-15T10:30:00Z",
data:   "backend_uuid": "<backend-uuid>",
data:   "status": "completed"
data: }
```

**Response fields**:
- `uuid` - Entry/message UUID
- `text_completed` - Full response text
- `blocks` - Structured content blocks
- `sources_list` - Citations with URLs
- `backend_uuid` - Backend processing UUID
- `created_at` - Timestamp
- `status` - Final status

### 5. `error`

Error information:

```
event: error
data: {
data:   "code": "rate_limit_exceeded",
data:   "message": "Rate limit exceeded. Please try again later.",
data:   "retry_after": 60
data: }
```

**Error codes**:
- `rate_limit_exceeded` - Too many requests
- `invalid_request` - Malformed request
- `authentication_failed` - Invalid auth token
- `service_unavailable` - Server error

## Connection Management

### Initial Connection

```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "https://www.perplexity.ai/rest/sse/perplexity.ask",
        json=request_payload,
        headers={
            "Cookie": f"__Secure-next-auth.session-token={token}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(60.0, connect=10.0),
    ) as response:
        async for line in response.aiter_lines():
            # Process SSE events
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                # Parse JSON and handle event
```

### Reconnection Strategy

**Cursor-Based Resumption**:

When a connection drops, reconnect with the last event ID:

```python
last_event_id = None

async def stream_with_reconnect(request_payload, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            headers = {
                "Cookie": f"__Secure-next-auth.session-token={token}",
                "Content-Type": "application/json",
            }
            if last_event_id:
                headers["Last-Event-ID"] = last_event_id
            
            async with client.stream("POST", url, json=request_payload, headers=headers) as response:
                async for event in parse_sse_events(response):
                    if event.id:
                        last_event_id = event.id
                    yield event
                    
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            retries += 1
            if retries >= max_retries:
                raise
            await asyncio.sleep(2 ** retries)  # Exponential backoff
```

### Exponential Backoff

Recommended backoff strategy:

```python
from typing import Callable, TypeVar
import asyncio
import random

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 30.0,
    jitter: float = 0.25
) -> T:
    """Retry function with exponential backoff and jitter."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Calculate backoff with exponential growth and jitter
            backoff = min(initial_backoff * (2 ** attempt), max_backoff)
            jitter_amount = backoff * jitter * random.random()
            sleep_time = backoff + jitter_amount
            
            await asyncio.sleep(sleep_time)
```

## Protocol Versions

### Version Evolution

| Version | Release | Key Changes |
|---------|---------|-------------|
| 2.17 | 2023 Q4 | Initial SSE streaming |
| 2.18 | 2024 Q1 | JSON Patch support, enhanced error handling |

### Version Detection

The pplx-unofficial-sdk tracks protocol versions by monitoring:

1. **Service Worker Chunks**: JavaScript files include version info
2. **API Responses**: Version headers in responses
3. **Error Messages**: Version mismatch errors

**Best Practice**: Always send the latest supported version in requests.

## Advanced Features

### JSON Patch Support (Protocol 2.18+)

Instead of sending complete chunks, the server can send diffs using the `delta` field in `answer_chunk` events:

```
event: answer_chunk
data: {
data:   "delta": {
data:     "op": "add",
data:     "path": "/text/42",
data:     "value": "quantum "
data:   }
data: }
```

This follows [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html) JSON Patch specification.

**JSON Patch Operations**:
- `add` - Add value at path
- `remove` - Remove value at path
- `replace` - Replace value at path
- `move` - Move value from one path to another
- `copy` - Copy value from one path to another
- `test` - Test that a value at path equals specified value

**Example** (using `answer_chunk` event with `delta` field):
```
event: answer_chunk
data: {
data:   "delta": {
data:     "op": "add",
data:     "path": "/text/42",
data:     "value": "quantum "
data:   }
data: }
```

### Rate Limiting

**Rate Limit Headers** (in HTTP response):

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Handling Rate Limits**:

```python
async def stream_with_rate_limit(request_payload):
    try:
        async for event in stream_ask(request_payload):
            yield event
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 60))
            await asyncio.sleep(retry_after)
            # Retry request
            async for event in stream_ask(request_payload):
                yield event
```

### CSRF Protection

The API uses state parameters for CSRF protection:

```python
import secrets

# Generate CSRF token
csrf_token = secrets.token_urlsafe(32)

request_payload = {
    "query": "...",
    "state": csrf_token,  # Include in request
    # ... other fields
}

# Server echoes back in response
# Verify: response["state"] == csrf_token
```

## Implementation Examples

### Python (Current pplx-sdk)

```python
from pplx_sdk import PerplexityClient

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

conv = client.new_conversation(title="Research")

# Stream response
for chunk in conv.ask_stream("Explain quantum computing"):
    if chunk.type == "answer_chunk":
        print(chunk.text, end="", flush=True)
    elif chunk.type == "final_response":
        print(f"\n\nSources: {len(chunk.sources_list)}")
```

### TypeScript (pplx-unofficial-sdk)

```typescript
import { createPplxClient } from "@pplx-unofficial/sdk";

const client = createPplxClient();

// Stream search
for await (const entry of client.search("Explain quantum computing", {
    focus: "academic",
    model: "sonar-pro"
})) {
    console.log("Status:", entry.status);
    
    if (entry.status === "STREAMING") {
        process.stdout.write(entry.textChunk);
    }
    
    if (entry.final) {
        console.log("\n\nSources:", entry.sources_list.length);
    }
}
```

## Debugging Tips

### 1. Capture Raw SSE Stream

```python
async with client.stream("POST", url, json=payload) as response:
    async for line in response.aiter_lines():
        print(f"RAW: {line}")  # Log every line
```

### 2. Monitor Connection State

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pplx_sdk.sse")

# Logs will show:
# - Connection establishment
# - Event types received
# - Reconnection attempts
# - Error conditions
```

### 3. Validate Event Sequence

Expected sequence for a successful request:

```
1. query_progress (status: "searching")
2. search_results (list of URLs)
3. query_progress (status: "generating")
4. answer_chunk (multiple, streaming text)
5. final_response (complete entry with metadata)
```

If this sequence is interrupted, check:
- Network connectivity
- Authentication token validity
- Rate limit status
- Server-side errors

## Performance Considerations

### Connection Pooling

Reuse HTTP connections for multiple requests:

```python
# Create persistent client
client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=10),
    timeout=httpx.Timeout(60.0),
)

# Reuse for multiple streams
async for event in stream_ask(client, payload1):
    ...
    
async for event in stream_ask(client, payload2):
    ...
```

### Buffer Management

For high-throughput streaming, use buffering:

```python
from collections import deque

chunk_buffer = deque(maxlen=100)  # Limit memory usage

async for chunk in stream:
    chunk_buffer.append(chunk)
    # Process in batches
    if len(chunk_buffer) >= 10:
        process_batch(list(chunk_buffer))
        chunk_buffer.clear()
```

## References

- **SSE Specification (WHATWG HTML)**: [Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- **SSE over HTTP/2**: [RFC 8895](https://www.rfc-editor.org/rfc/rfc8895.html)
- **JSON Patch**: [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html)
- **pplx-unofficial-sdk**: [GitHub Repository](https://github.com/pv-udpv/pplx-unofficial-sdk)
- **HTTP/2 Server Push**: [RFC 7540 Section 8.2](https://www.rfc-editor.org/rfc/rfc7540.html#section-8.2)

## See Also

- [Architecture Overview](./ARCHITECTURE.md)
- [REST API Guide](./REST_API.md)
- [OAuth Connectors Guide](./OAUTH_CONNECTORS.md)
