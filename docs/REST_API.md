# REST API Guide

> Comprehensive REST API documentation for Perplexity AI, synthesized from @pv-udpv/pplx-unofficial-sdk research

## Overview

The Perplexity AI REST API provides CRUD operations for threads, entries, and collections. This complements the SSE streaming API with persistent storage and management capabilities.

## Base URL

```
https://www.perplexity.ai/rest
```

## Authentication

All REST API requests require authentication via session token:

```
Cookie: __Secure-next-auth.session-token=<your-token>
```

**Alternative (Authorization header)**:
```
Authorization: Bearer <your-token>
```

## API Endpoints

### Thread Management

#### List Threads

```http
GET /rest/threads?limit=20&offset=0&sort=updated_at
```

**Query Parameters**:
- `limit` (int): Number of threads to return (default: 20, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `sort` (string): Sort field (`created_at`, `updated_at`, `title`)
- `order` (string): Sort order (`asc`, `desc`)

**Response**:
```json
{
  "items": [
    {
      "uuid": "<thread-uuid>",
      "title": "Research Thread",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z",
      "entry_count": 5,
      "access": "private"
    }
  ],
  "total": 42,
  "has_more": true
}
```

#### Get Thread

```http
GET /rest/threads/<thread-uuid>
```

**Response**:
```json
{
  "uuid": "<thread-uuid>",
  "title": "Research Thread",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "entries": [
    {
      "uuid": "<entry-uuid>",
      "text_completed": "...",
      "created_at": "2024-01-15T10:01:00Z",
      "role": "assistant",
      "sources_list": []
    }
  ],
  "access": "private",
  "collection_uuids": ["<collection-uuid>"]
}
```

#### Create Thread

```http
POST /rest/threads
Content-Type: application/json

{
  "title": "New Research Thread",
  "access": "private"
}
```

**Request Body**:
- `title` (string, required): Thread title
- `access` (string, optional): Access level (`private`, `org`, `public`)

**Response** (201 Created):
```json
{
  "uuid": "<thread-uuid>",
  "title": "New Research Thread",
  "created_at": "2024-01-15T10:00:00Z",
  "access": "private"
}
```

#### Update Thread

```http
PATCH /rest/threads/<thread-uuid>
Content-Type: application/json

{
  "title": "Updated Title",
  "access": "org"
}
```

**Supported Operations** (JSON Patch):
```json
[
  {
    "op": "replace",
    "path": "/title",
    "value": "New Title"
  },
  {
    "op": "replace",
    "path": "/access",
    "value": "public"
  }
]
```

#### Delete Thread

```http
DELETE /rest/threads/<thread-uuid>
```

**Response** (204 No Content)

### Entry Management

#### Get Entry

```http
GET /rest/entries/<entry-uuid>
```

**Response**:
```json
{
  "uuid": "<entry-uuid>",
  "thread_uuid": "<thread-uuid>",
  "backend_uuid": "<backend-uuid>",
  "text_query": "User question",
  "text_completed": "AI response...",
  "blocks": [
    {
      "type": "text",
      "content": "AI response..."
    }
  ],
  "sources_list": [
    {
      "title": "Example",
      "url": "https://example.com",
      "citation_index": 1
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "role": "assistant",
  "model": "pplx-70b-chat"
}
```

#### Fork Entry

Create a new thread from an existing entry:

```http
POST /rest/entries/<entry-uuid>/fork
Content-Type: application/json

{
  "title": "Forked Thread",
  "access": "private"
}
```

**Response** (201 Created):
```json
{
  "thread_uuid": "<new-thread-uuid>",
  "entry_uuid": "<new-entry-uuid>",
  "title": "Forked Thread"
}
```

#### Like Entry

```http
POST /rest/entries/<entry-uuid>/like
```

**Response** (200 OK):
```json
{
  "liked": true,
  "like_count": 42
}
```

#### Unlike Entry

```http
DELETE /rest/entries/<entry-uuid>/like
```

**Response** (200 OK):
```json
{
  "liked": false,
  "like_count": 41
}
```

### Collection Management (Spaces)

#### List Collections

```http
GET /rest/collections?limit=20&offset=0
```

**Response**:
```json
{
  "items": [
    {
      "uuid": "<collection-uuid>",
      "name": "AI Research",
      "description": "Collection of AI threads",
      "created_at": "2024-01-15T10:00:00Z",
      "thread_count": 12,
      "access": "org"
    }
  ],
  "total": 5,
  "has_more": false
}
```

#### Get Collection

```http
GET /rest/collections/<collection-uuid>
```

**Response**:
```json
{
  "uuid": "<collection-uuid>",
  "name": "AI Research",
  "description": "Collection of AI threads",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "threads": [
    {
      "uuid": "<thread-uuid>",
      "title": "Thread 1",
      "entry_count": 5
    }
  ],
  "access": "org",
  "owner_uuid": "<user-uuid>"
}
```

#### Create Collection

```http
POST /rest/collections
Content-Type: application/json

{
  "name": "New Collection",
  "description": "Description here",
  "access": "private"
}
```

**Response** (201 Created):
```json
{
  "uuid": "<collection-uuid>",
  "name": "New Collection",
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Update Collection

```http
PATCH /rest/collections/<collection-uuid>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "New description"
}
```

#### Delete Collection

```http
DELETE /rest/collections/<collection-uuid>
```

**Response** (204 No Content)

#### Add Thread to Collection

```http
POST /rest/collections/<collection-uuid>/threads
Content-Type: application/json

{
  "thread_uuid": "<thread-uuid>"
}
```

**Response** (200 OK):
```json
{
  "collection_uuid": "<collection-uuid>",
  "thread_uuid": "<thread-uuid>",
  "added_at": "2024-01-15T10:00:00Z"
}
```

#### Remove Thread from Collection

```http
DELETE /rest/collections/<collection-uuid>/threads/<thread-uuid>
```

**Response** (204 No Content)

## Pagination

### Offset-Based Pagination

```http
GET /rest/threads?limit=20&offset=40
```

**Response includes**:
```json
{
  "items": [...],
  "total": 100,
  "has_more": true,
  "next_offset": 60
}
```

### Cursor-Based Pagination (Advanced)

For large datasets, use cursor-based pagination:

```http
GET /rest/threads?limit=20&cursor=<cursor-token>
```

**Response**:
```json
{
  "items": [...],
  "next_cursor": "<next-cursor-token>",
  "has_more": true
}
```

### Implementation Example (Python)

```python
async def list_all_threads(client):
    """Paginate through all threads."""
    offset = 0
    limit = 50
    
    while True:
        response = await client.get(
            "/rest/threads",
            params={"limit": limit, "offset": offset}
        )
        
        for thread in response["items"]:
            yield thread
        
        if not response["has_more"]:
            break
        
        offset += limit
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "not_found",
    "message": "Thread not found",
    "details": {
      "resource": "thread",
      "uuid": "<thread-uuid>"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary unavailability |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `authentication_failed` | 401 | Invalid auth token |
| `not_found` | 404 | Resource not found |
| `validation_error` | 400 | Invalid input data |
| `rate_limit_exceeded` | 429 | Too many requests |
| `conflict` | 409 | Resource already exists |
| `forbidden` | 403 | Access denied |
| `internal_error` | 500 | Server error |

### Retry Strategy

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_request(
    func: Callable[..., T],
    max_retries: int = 3,
    retryable_status: set[int] = {429, 500, 502, 503, 504}
) -> T:
    """Retry REST API requests with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPStatusError as e:
            if e.response.status_code not in retryable_status:
                raise
            
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff
            backoff = 2 ** attempt
            await asyncio.sleep(backoff)
```

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Rate Limit Strategy

```python
import time

class RateLimiter:
    def __init__(self, max_requests: int, window: float):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    async def acquire(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove expired requests
        self.requests = [r for r in self.requests if now - r < self.window]
        
        if len(self.requests) >= self.max_requests:
            # Calculate sleep time
            oldest = self.requests[0]
            sleep_time = self.window - (now - oldest)
            await asyncio.sleep(sleep_time)
            return await self.acquire()
        
        self.requests.append(now)

# Usage
limiter = RateLimiter(max_requests=100, window=60.0)  # 100 req/min

async def make_request():
    await limiter.acquire()
    return await client.get("/rest/threads")
```

## Advanced Features

### JSON Patch Updates

Use [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html) JSON Patch for partial updates:

```http
PATCH /rest/threads/<thread-uuid>
Content-Type: application/json-patch+json

[
  {
    "op": "replace",
    "path": "/title",
    "value": "New Title"
  },
  {
    "op": "add",
    "path": "/tags/-",
    "value": "ai"
  }
]
```

**Operations**:
- `add` - Add value
- `remove` - Remove value
- `replace` - Replace value
- `move` - Move value
- `copy` - Copy value
- `test` - Test value equality

### Conditional Requests

Use ETags for optimistic concurrency control:

```http
GET /rest/threads/<thread-uuid>
```

**Response includes**:
```
ETag: "abc123"
```

**Update with condition**:
```http
PATCH /rest/threads/<thread-uuid>
If-Match: "abc123"
Content-Type: application/json

{"title": "New Title"}
```

If the resource changed (ETag mismatch):
```
HTTP/1.1 412 Precondition Failed
```

### Bulk Operations

Perform batch operations in a single request:

```http
POST /rest/bulk
Content-Type: application/json

{
  "operations": [
    {
      "method": "GET",
      "path": "/threads/<uuid1>"
    },
    {
      "method": "PATCH",
      "path": "/threads/<uuid2>",
      "body": {"title": "New Title"}
    }
  ]
}
```

**Response**:
```json
{
  "results": [
    {
      "status": 200,
      "body": {"uuid": "<uuid1>", ...}
    },
    {
      "status": 200,
      "body": {"uuid": "<uuid2>", ...}
    }
  ]
}
```

## Implementation Examples

### Python (pplx-sdk) - Planned API

> **Note**: The following methods are planned for future implementation. Currently, pplx-sdk focuses on SSE streaming via the `Conversation` API. REST CRUD operations can be accessed via direct HTTP calls.

**Planned high-level API** (not yet implemented):
```python
from pplx_sdk import PerplexityClient

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

# Planned: List threads
threads = await client.list_threads(limit=20, sort="updated_at")

# Planned: Create thread
thread = await client.create_thread(title="Research")

# Planned: Update thread
await client.update_thread(thread.uuid, title="Updated Title")

# Planned: Delete thread
await client.delete_thread(thread.uuid)

# Planned: Get entry
entry = await client.get_entry(entry_uuid)

# Planned: Like entry
await client.like_entry(entry_uuid)

# Planned: Fork entry
new_thread = await client.fork_entry(entry_uuid, title="Fork")
```

**Current working API** (direct HTTP calls):
```python
from pplx_sdk import PerplexityClient
import httpx

client = PerplexityClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

# Access the underlying HTTP client
http_client = client.http_client

# List threads
response = http_client.get("/rest/threads", params={"limit": 20})
threads = response.json()

# Create thread
response = http_client.post("/rest/threads", json={"title": "Research"})
thread = response.json()

# Get entry
response = http_client.get(f"/rest/entries/{entry_uuid}")
entry = response.json()

# Like entry
http_client.post(f"/rest/entries/{entry_uuid}/like")
```

### TypeScript (pplx-unofficial-sdk)

```typescript
import { createRestClient } from "@pplx-unofficial/sdk";

const rest = createRestClient();

// List threads
const threads = await rest.listThreads({ 
    limit: 20, 
    sort: "updated_at" 
});

// Create thread
const thread = await rest.createThread({
    title: "Research"
});

// Update thread
await rest.updateThread(thread.uuid, {
    title: "Updated Title"
});

// Delete thread
await rest.deleteThread(thread.uuid);

// Get entry
const entry = await rest.getEntry(entryUuid);

// Like entry
await rest.likeEntry(entryUuid);

// Fork entry
const newThread = await rest.forkEntry({
    backend_uuid: entryUuid,
    title: "Fork"
});
```

## Best Practices

### 1. Use Connection Pooling

```python
import httpx

client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
    timeout=httpx.Timeout(30.0)
)
```

### 2. Implement Retry Logic

Always retry transient errors (429, 5xx):

```python
from pplx_sdk.shared.retry import retry_with_backoff, RetryConfig

config = RetryConfig(max_retries=3, initial_backoff_ms=1000)

result = await retry_with_backoff(
    lambda: client.get("/rest/threads"),
    config=config,
    retryable_exceptions=(httpx.TimeoutException, httpx.NetworkError)
)
```

### 3. Handle Rate Limits Gracefully

```python
async def make_request_with_rate_limit():
    try:
        return await client.get("/rest/threads")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 60))
            await asyncio.sleep(retry_after)
            return await client.get("/rest/threads")
        raise
```

### 4. Use Pagination for Large Datasets

```python
async def fetch_all_threads():
    offset = 0
    limit = 100  # Max per page
    all_threads = []
    
    while True:
        batch = await client.get(
            "/rest/threads",
            params={"limit": limit, "offset": offset}
        )
        all_threads.extend(batch["items"])
        
        if not batch["has_more"]:
            break
        
        offset += limit
    
    return all_threads
```

### 5. Close Connections Properly

```python
async with httpx.AsyncClient() as client:
    # Use client
    threads = await client.get("/rest/threads")
# Client automatically closed
```

## References

- [pplx-unofficial-sdk GitHub](https://github.com/pv-udpv/pplx-unofficial-sdk)
- [HTTP/1.1 Specification](https://www.rfc-editor.org/rfc/rfc7231.html)
- [JSON Patch RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html)
- [ETag RFC 7232](https://www.rfc-editor.org/rfc/rfc7232.html)

## See Also

- [SSE Streaming Guide](./SSE_STREAMING.md)
- [OAuth Connectors Guide](./OAUTH_CONNECTORS.md)
- [Architecture Overview](./ARCHITECTURE.md)
