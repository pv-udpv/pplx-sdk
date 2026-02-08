# OAuth Connectors Guide

> Comprehensive guide to OAuth connectors in Perplexity AI, synthesized from @pv-udpv/pplx-unofficial-sdk research

## Overview

Perplexity AI supports OAuth connectors for integrating with external file storage and productivity services. This enables search across documents from Google Drive, Notion, OneDrive, and other platforms.

## Supported Connectors

### Connector Matrix

| Connector | Type | Plan | OAuth Flow | File Import | Sync | Status |
|-----------|------|------|------------|-------------|------|--------|
| Google Drive | File Storage | Pro+ | Yes | Yes | Real-time | Active |
| Microsoft OneDrive | File Storage | Enterprise | Yes | Yes | Yes | Active |
| SharePoint | File Storage | Enterprise | Yes | Yes | Org-wide | Active |
| Dropbox | File Storage | Enterprise | Yes | Yes | Yes | Active |
| Box | File Storage | Enterprise | Yes | Yes | Yes | Active |
| Notion | Productivity | Pro+ | Yes | Database | Yes | Active |
| Confluence | Productivity | Enterprise | Yes | Space | Yes | Active |
| Slack | Communication | Enterprise | Yes | Channel | Historical | Active |
| Local Upload | Local | All | N/A | Yes | No | Active |

### Plan Requirements

- **Pro+**: Google Drive, Notion, Local Upload
- **Enterprise**: All connectors

## OAuth Flow

### 1. Authorization Request

Start OAuth flow by requesting authorization URL:

```http
POST /rest/connectors/<connector-id>/authorize
Content-Type: application/json

{
  "redirect_uri": "https://www.perplexity.ai/oauth/callback",
  "state": "<csrf-token>",
  "scopes": ["drive.readonly", "drive.metadata.readonly"]
}
```

**Parameters**:
- `connector-id`: Connector identifier (e.g., `google_drive`, `notion`)
- `redirect_uri`: OAuth callback URL (must be whitelisted)
- `state`: CSRF protection token (generated client-side)
- `scopes`: OAuth scopes (connector-specific)

**Response**:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "<csrf-token>",
  "expires_in": 600
}
```

### 2. User Authorization (Browser)

Redirect user to `auth_url`:

```typescript
// Open popup or redirect
window.open(auth_url, "_blank", "width=600,height=700");

// Or use popup manager
const popup = new OAuthPopupManager();
await popup.authorize(auth_url);
```

### 3. OAuth Callback

After user grants access, OAuth provider redirects to callback URL:

```
https://www.perplexity.ai/oauth/callback?
  code=<auth-code>&
  state=<csrf-token>
```

### 4. Token Exchange

Exchange authorization code for access token:

```http
POST /rest/connectors/<connector-id>/token
Content-Type: application/json

{
  "code": "<auth-code>",
  "state": "<csrf-token>",
  "redirect_uri": "https://www.perplexity.ai/oauth/callback"
}
```

**Response**:
```json
{
  "access_token": "<encrypted-token>",
  "refresh_token": "<encrypted-refresh-token>",
  "expires_in": 3600,
  "connector_id": "google_drive",
  "user_info": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

**Security Note**: Tokens are encrypted server-side with AES-256-GCM.

## Connector Management

### Get Connector Status

```http
GET /rest/connectors
```

**Response**:
```json
{
  "connectors": [
    {
      "id": "google_drive",
      "name": "Google Drive",
      "type": "file_storage",
      "connected": true,
      "user_email": "user@example.com",
      "connected_at": "2024-01-15T10:00:00Z",
      "expires_at": "2024-01-15T11:00:00Z",
      "scopes": ["drive.readonly"],
      "capabilities": ["picker", "sync", "search"]
    },
    {
      "id": "notion",
      "name": "Notion",
      "type": "productivity",
      "connected": false
    }
  ]
}
```

### Disconnect Connector

```http
DELETE /rest/connectors/<connector-id>
```

**Response** (204 No Content)

### Refresh Token

Automatically refresh expired tokens:

```http
POST /rest/connectors/<connector-id>/refresh
```

**Response**:
```json
{
  "access_token": "<new-encrypted-token>",
  "expires_in": 3600
}
```

## File Operations

### List Files

```http
GET /rest/connectors/<connector-id>/files?limit=100&cursor=<cursor>
```

**Query Parameters**:
- `limit` (int): Max results per page (default: 50, max: 100)
- `cursor` (string): Pagination cursor
- `folder_id` (string): Filter by folder (optional)
- `query` (string): Search query (optional)

**Response**:
```json
{
  "files": [
    {
      "id": "<file-id>",
      "name": "Document.pdf",
      "mimeType": "application/pdf",
      "size": 1024000,
      "modified_at": "2024-01-15T10:00:00Z",
      "url": "https://drive.google.com/file/...",
      "thumbnail_url": "https://...",
      "parent_id": "<folder-id>",
      "synced": false
    }
  ],
  "next_cursor": "<next-cursor>",
  "has_more": true
}
```

### File Picker

Open file picker UI:

```http
POST /rest/connectors/<connector-id>/picker
Content-Type: application/json

{
  "multiple": true,
  "mime_types": ["application/pdf", "text/plain"],
  "max_files": 10
}
```

**Response**:
```json
{
  "picker_url": "https://accounts.google.com/picker?...",
  "session_id": "<picker-session-id>"
}
```

### Sync Files to Space

Import files into a Perplexity Space (Collection):

```http
POST /rest/connectors/<connector-id>/sync
Content-Type: application/json

{
  "file_ids": ["<file-id-1>", "<file-id-2>"],
  "collection_uuid": "<collection-uuid>",
  "sync_mode": "manual"
}
```

**Parameters**:
- `file_ids`: Array of file IDs to sync
- `collection_uuid`: Target collection UUID
- `sync_mode`: `manual` or `auto` (real-time sync)

**Response**:
```json
{
  "sync_job_id": "<job-uuid>",
  "status": "pending",
  "file_count": 2,
  "estimated_time": 30
}
```

### Check Sync Status

```http
GET /rest/connectors/<connector-id>/sync/<job-id>
```

**Response**:
```json
{
  "job_id": "<job-uuid>",
  "status": "completed",
  "progress": 100,
  "files_synced": 2,
  "files_failed": 0,
  "completed_at": "2024-01-15T10:01:00Z"
}
```

**Status values**:
- `pending` - Job queued
- `processing` - Importing files
- `completed` - All files imported
- `failed` - Job failed
- `partial` - Some files failed

## Connector-Specific Details

### Google Drive

**OAuth Scopes**:
```json
[
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/drive.metadata.readonly"
]
```

**Supported File Types**:
- Documents: PDF, DOCX, TXT, MD
- Spreadsheets: XLSX, CSV, Google Sheets
- Presentations: PPTX, Google Slides
- Others: Images (OCR), HTML

**Special Features**:
- Real-time sync with webhook
- File picker integration
- Shared drive support
- Version history access

### Notion

**OAuth Scopes**:
```json
[
  "read_content"
]
```

**Supported Resources**:
- Pages
- Databases
- Blocks

**Special Features**:
- Database query support
- Block-level content extraction
- Nested page support
- Real-time sync via webhooks

### Microsoft OneDrive

**OAuth Scopes**:
```json
[
  "Files.Read",
  "Files.Read.All"
]
```

**Supported File Types**:
- Office documents: DOCX, XLSX, PPTX
- PDFs and text files
- SharePoint lists

**Special Features**:
- SharePoint Online integration
- Organization-wide access (Enterprise)
- Real-time delta sync

### Dropbox

**OAuth Scopes**:
```json
[
  "files.metadata.read",
  "files.content.read"
]
```

**Supported File Types**:
- All document types
- Paper docs (native Dropbox format)

**Special Features**:
- Paper doc integration
- Shared folder support
- Team space access

### Slack

**OAuth Scopes**:
```json
[
  "channels:history",
  "channels:read",
  "users:read"
]
```

**Supported Resources**:
- Public channels
- Private channels (if bot is added)
- Direct messages (with permissions)

**Special Features**:
- Channel history search
- Message threading
- File attachments from Slack
- User mention resolution

## Implementation Examples

### Python (Future pplx-sdk)

```python
from pplx_sdk.connectors import ConnectorClient

# Initialize connector client
connectors = ConnectorClient(
    api_base="https://www.perplexity.ai",
    auth_token="<token>"
)

# Start OAuth flow
auth = await connectors.authorize("google_drive")
print(f"Visit: {auth.auth_url}")

# After callback, exchange code for token
token = await connectors.token("google_drive", code="<auth-code>")

# Get connector status
status = await connectors.status()
for conn in status.connectors:
    print(f"{conn.name}: {'connected' if conn.connected else 'disconnected'}")

# List files
files = await connectors.list_files(
    "google_drive",
    limit=50,
    folder_id="<folder-id>"
)

# Sync files to collection
job = await connectors.sync_files(
    "google_drive",
    file_ids=["<file-1>", "<file-2>"],
    collection_uuid="<collection-uuid>"
)

# Check sync progress
while job.status != "completed":
    job = await connectors.get_sync_status("google_drive", job.job_id)
    print(f"Progress: {job.progress}%")
    await asyncio.sleep(2)
```

### TypeScript (pplx-unofficial-sdk)

```typescript
import { createConnectorsClient, OAuthPopupManager } from "@pplx-unofficial/sdk";

const connectors = createConnectorsClient();

// Start OAuth flow
const auth = await connectors.authorize("google_drive");

// Open popup for user authorization
const popup = new OAuthPopupManager();
await popup.authorize(auth.auth_url);

// Get connector status
const status = await connectors.getConnectorsStatus();
console.log("Connected:", status.filter(c => c.connected));

// List files
const files = await connectors.listFiles("google_drive", { 
    limit: 100 
});

// Sync files to Space
await connectors.syncFiles(
    "google_drive",
    ["<file-1>", "<file-2>"],
    "<collection-uuid>"
);

// Disconnect
await connectors.disconnect("google_drive");
```

## Security Considerations

### 1. Token Encryption

All OAuth tokens are encrypted at rest:

**Encryption**:
- Algorithm: AES-256-GCM
- Key derivation: PBKDF2 with user-specific salt
- Per-user encryption keys

**Best Practice**: Never log or expose raw access tokens.

### 2. CSRF Protection

Always use state parameter:

```python
import secrets

# Generate CSRF token
state = secrets.token_urlsafe(32)

# Store in session
session["oauth_state"] = state

# Include in auth request
auth = await connectors.authorize("google_drive", state=state)

# Verify on callback
if callback_state != session["oauth_state"]:
    raise SecurityError("CSRF token mismatch")
```

### 3. Token Refresh

Automatically refresh tokens before expiry:

```python
async def ensure_valid_token(connector_id: str):
    """Ensure token is valid, refresh if needed."""
    status = await connectors.get_status(connector_id)
    
    if status.expires_at < datetime.now() + timedelta(minutes=5):
        # Token expires soon, refresh
        await connectors.refresh_token(connector_id)
```

### 4. Scope Minimization

Request only necessary scopes:

```python
# Good: Minimal scopes
scopes = ["drive.readonly"]

# Bad: Excessive permissions
scopes = ["drive", "drive.file", "drive.appdata"]
```

## Error Handling

### OAuth Errors

```json
{
  "error": "access_denied",
  "error_description": "User denied access",
  "state": "<csrf-token>"
}
```

**Common Errors**:
- `access_denied` - User rejected authorization
- `invalid_grant` - Invalid authorization code
- `invalid_scope` - Unsupported scopes
- `token_expired` - Access token expired

### Connector Errors

```json
{
  "error": {
    "code": "connector_error",
    "message": "Failed to fetch files from Google Drive",
    "details": {
      "connector_id": "google_drive",
      "error_type": "api_error",
      "retry_after": 60
    }
  }
}
```

### Retry Strategy

```python
async def retry_connector_request(func, max_retries=3):
    """Retry connector operations with backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except ConnectorError as e:
            if e.code == "token_expired":
                # Refresh token and retry
                await connectors.refresh_token(e.connector_id)
                continue
            elif e.code == "rate_limit":
                # Respect rate limit
                await asyncio.sleep(e.retry_after)
                continue
            elif attempt == max_retries - 1:
                raise
            
            # Exponential backoff
            await asyncio.sleep(2 ** attempt)
```

## Best Practices

### 1. Popup Manager for OAuth

Use popup instead of redirect for better UX:

```typescript
class OAuthPopupManager {
    async authorize(authUrl: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const popup = window.open(
                authUrl,
                "oauth",
                "width=600,height=700,left=100,top=100"
            );
            
            // Listen for callback
            window.addEventListener("message", (event) => {
                if (event.data.type === "oauth_callback") {
                    popup?.close();
                    resolve(event.data.code);
                }
            });
        });
    }
}
```

### 2. Connector Status Polling

Keep connector status up-to-date:

```python
async def monitor_connectors():
    """Poll connector status every 5 minutes."""
    while True:
        try:
            status = await connectors.get_status()
            # Update UI or cache
            update_connector_ui(status)
        except Exception as e:
            logger.error(f"Failed to fetch connector status: {e}")
        
        await asyncio.sleep(300)  # 5 minutes
```

### 3. Sync Progress UI

Show real-time sync progress:

```typescript
async function syncWithProgress(files: string[], collection: string) {
    const job = await connectors.syncFiles("google_drive", files, collection);
    
    while (job.status !== "completed") {
        // Update progress bar
        updateProgressBar(job.progress);
        
        await sleep(2000);
        job = await connectors.getSyncStatus("google_drive", job.job_id);
    }
    
    console.log(`Synced ${job.files_synced} files`);
}
```

## References

- [OAuth 2.0 RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)
- [Google Drive API](https://developers.google.com/drive/api/v3)
- [Notion API](https://developers.notion.com/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [pplx-unofficial-sdk GitHub](https://github.com/pv-udpv/pplx-unofficial-sdk)

## See Also

- [REST API Guide](./REST_API.md)
- [SSE Streaming Guide](./SSE_STREAMING.md)
- [Architecture Overview](./ARCHITECTURE.md)
