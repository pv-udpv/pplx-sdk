# Quick Reference Guide

> Quick reference for Perplexity AI SDK development, synthesized from @pv-udpv repositories

## 📚 Documentation Index

| Document | Purpose | Size |
|----------|---------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Layered architecture, design patterns, microservices reference | 10.8KB |
| [SSE_STREAMING.md](./SSE_STREAMING.md) | Complete SSE protocol guide with reconnection | 13.2KB |
| [REST_API.md](./REST_API.md) | Full REST API reference with 24+ endpoints | 14.8KB |
| [OAUTH_CONNECTORS.md](./OAUTH_CONNECTORS.md) | OAuth integration for 9+ services | 14.5KB |
| [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md) | Integration summary and roadmap | 12.8KB |

## 🔑 Key Concepts

### Protocol Version: 2.17-2.18

**Total Endpoints**: 38+
- 2 SSE streaming endpoints
- 24 REST API endpoints
- 11 OAuth connector endpoints
- 1 Service worker endpoint

### Architecture Layers

```
Client/Application    ← High-level API (PerplexityClient)
       ↓
Domain/Business       ← Threads, Entries, Collections
       ↓
Transport/Streaming   ← HTTP, SSE, WebSocket
       ↓
Shared Utilities      ← Retry, Auth, Logging
       ↓
Core (Protocols)      ← Base abstractions
```

### SSE Event Types

1. **query_progress** - Search status updates
2. **search_results** - Web search results with citations
3. **answer_chunk** - Incremental AI response tokens
4. **final_response** - Complete response with metadata
5. **error** - Error information

## 🚀 Quick Start Examples

### SSE Streaming (Python)

```python
from pplx_sdk import PerplexityClient

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

conv = client.new_conversation(title="Research")

for chunk in conv.ask_stream("Explain quantum computing"):
    if chunk.type == "answer_chunk":
        print(chunk.text, end="", flush=True)
    elif chunk.type == "final_response":
        print(f"\n\nSources: {len(chunk.sources_list)}")
```

### REST API (Python) - Current Implementation

> **Note**: High-level REST methods like `list_threads()` are planned but not yet implemented. Use direct HTTP calls:

```python
from pplx_sdk import PerplexityClient

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

# Access HTTP client for direct REST calls
http = client.http_client

# List threads
response = http.get("/rest/threads", params={"limit": 20, "sort": "updated_at"})
threads = response.json()

# Create thread
response = http.post("/rest/threads", json={"title": "Research"})
thread = response.json()

# Get entry
response = http.get(f"/rest/entries/{entry_uuid}")
entry = response.json()

# Like entry
http.post(f"/rest/entries/{entry_uuid}/like")
```

## 🔄 Common Patterns

### Retry with Exponential Backoff

```python
from pplx_sdk.shared.retry import retry_with_backoff, RetryConfig

config = RetryConfig(max_retries=3, initial_backoff_ms=1000)

result = await retry_with_backoff(
    lambda: client.get("/rest/threads"),
    config=config,
    retryable_exceptions=(httpx.TimeoutException,)
)
```

### Pagination

```python
# Offset-based
offset = 0
while True:
    batch = await client.list_threads(limit=50, offset=offset)
    for thread in batch.items:
        process(thread)
    if not batch.has_more:
        break
    offset += 50
```

### Rate Limiting

```python
async def with_rate_limit(func):
    try:
        return await func()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 60))
            await asyncio.sleep(retry_after)
            return await func()
        raise
```

## 🔐 OAuth Connectors (Planned Feature)

> **Note**: OAuth connector support is a planned feature for pplx-sdk. The following is based on the pplx-unofficial-sdk TypeScript implementation and serves as a reference for future implementation.

### Supported Services (Reference)

| Service | Type | OAuth Flow | File Operations |
|---------|------|------------|-----------------|
| Google Drive | Storage | ✅ | List, Picker, Sync |
| Notion | Productivity | ✅ | Database, Pages |
| OneDrive | Storage | ✅ | List, Sync |
| Dropbox | Storage | ✅ | List, Sync |
| Slack | Communication | ✅ | Channel History |

### OAuth Flow (Planned API)

```python
# Future API - not yet implemented in pplx-sdk
from pplx_sdk.connectors import ConnectorClient

connectors = ConnectorClient(auth_token="<token>")

# 1. Start authorization
auth = await connectors.authorize("google_drive")

# 2. User authorizes (browser redirect)

# 3. Exchange code for token
token = await connectors.token("google_drive", code="<auth-code>")

# 4. List files
files = await connectors.list_files("google_drive", limit=50)

# 5. Sync to collection
await connectors.sync_files("google_drive", file_ids, collection_uuid)
```

## 🛠️ Implementation Roadmap

### High Priority

1. **Update Protocol Version** (2.17 → 2.18)
2. **Enhanced REST API** (forking, collections, JSON Patch)
3. **Rate Limiting** (built-in rate limiter)

### Medium Priority

4. **OAuth Connectors** (Google Drive, Notion first)
5. **JSON Patch Support** (RFC 6902)
6. **Advanced Reconnection** (cursor-based resumption)

### Low Priority (Reference)

7. **Service Worker Analysis** (version detection)
8. **Microservices Architecture** (scaling reference)

## 📊 Comparison: Python vs TypeScript

| Feature | pplx-sdk (Python) | pplx-unofficial-sdk (TypeScript) |
|---------|-------------------|----------------------------------|
| Language | Python 3.12+ | TypeScript 5.3+ |
| SSE Streaming | ✅ | ✅ |
| REST API | ✅ Core | ✅ Extended |
| OAuth | ❌ | ✅ 9+ connectors |
| Protocol | 2.17 | 2.18 |
| Rate Limiting | Basic | Advanced |

## 🔗 External References

- [pplx-unofficial-sdk GitHub](https://github.com/pv-udpv/pplx-unofficial-sdk)
- [Perplexity Official Docs](https://docs.perplexity.ai/)
- [SSE RFC 8895](https://www.rfc-editor.org/rfc/rfc8895.html)
- [JSON Patch RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html)
- [OAuth 2.0 RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)

## 🎯 Best Practices

1. **Use Connection Pooling** - Reuse HTTP connections
2. **Implement Retry Logic** - Always retry transient errors
3. **Handle Rate Limits** - Respect `Retry-After` headers
4. **Use Pagination** - For large datasets
5. **Close Connections** - Use context managers
6. **Validate Protocol** - Check protocol version
7. **Monitor Tokens** - Refresh before expiry
8. **Buffer Streaming** - For high-throughput

## 📝 Next Steps

To implement knowledge from this research:

1. Read [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md) for complete summary
2. Review specific guides based on feature area
3. Check implementation recommendations
4. Follow code patterns from examples
5. Reference TypeScript SDK for inspiration

---

**Last Updated**: 2024-02-08  
**Source**: @pv-udpv/perplexity-ai-unofficial, @pv-udpv/pplx-unofficial-sdk  
**Maintainer**: pplx-sdk team
