# Documentation Index

> Complete documentation for pplx-sdk with knowledge from @pv-udpv repositories

## 📖 Documentation Overview

This documentation synthesizes knowledge from multiple sources:
- @pv-udpv/pplx-unofficial-sdk (TypeScript SDK, Protocol 2.18)
- @pv-udpv/perplexity-ai-unofficial (Early Python wrapper)
- pplx-sdk repository (Current Python implementation)

**Total Documentation**: 2,978 lines (73KB) across 6 comprehensive guides

## 📚 Documentation Files

### Core Guides

#### 1. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Start Here! 📌
*Quick reference for common tasks and patterns*

**Best for**: Quick lookups, code snippets, getting started  
**Size**: 6.1KB | 221 lines  
**Topics**: Key concepts, quick start examples, common patterns, best practices

#### 2. [ARCHITECTURE.md](./ARCHITECTURE.md)
*Layered architecture, design patterns, and system design*

**Best for**: Understanding SDK structure, architectural decisions  
**Size**: 11KB | 388 lines  
**Topics**: 
- Layered architecture (core → shared → transport → domain → client)
- Protocol-oriented design patterns
- Async-first architecture
- Microservices reference architecture
- Comparison: Python vs TypeScript SDK

#### 3. [SSE_STREAMING.md](./SSE_STREAMING.md)
*Complete Server-Sent Events streaming protocol guide*

**Best for**: Implementing streaming, debugging SSE issues  
**Size**: 13KB | 557 lines  
**Topics**:
- SSE protocol basics
- Perplexity SSE endpoint (`/rest/sse/perplexity.ask`)
- Five event types (query_progress, search_results, answer_chunk, final_response, error)
- Connection management and reconnection strategies
- Protocol versions (2.17 → 2.18)
- JSON Patch support (RFC 6902)
- Rate limiting and backoff strategies

#### 4. [REST_API.md](./REST_API.md)
*Full REST API reference with 24+ endpoints*

**Best for**: Implementing CRUD operations, API integration  
**Size**: 15KB | 709 lines  
**Topics**:
- Thread management (list, get, create, update, delete)
- Entry operations (get, fork, like/unlike)
- Collection management (Spaces)
- Pagination (offset-based and cursor-based)
- Error handling and status codes
- JSON Patch updates
- Conditional requests with ETags
- Bulk operations

#### 5. [OAUTH_CONNECTORS.md](./OAUTH_CONNECTORS.md)
*OAuth integration for 9+ external services*

**Best for**: Planning OAuth features, understanding connectors  
**Size**: 15KB | 698 lines  
**Topics**:
- 9+ connectors (Google Drive, Notion, OneDrive, Dropbox, Slack, etc.)
- OAuth 2.0 flow implementation
- File operations (list, picker, sync)
- Token encryption (AES-256-GCM)
- Connector-specific capabilities
- Security considerations (CSRF, token refresh)

#### 6. [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md)
*Integration summary and implementation roadmap*

**Best for**: Understanding what was learned, planning future work  
**Size**: 13KB | 505 lines  
**Topics**:
- Source repository overview
- Knowledge areas integrated
- Comparison matrix (Python vs TypeScript)
- Implementation recommendations (high/medium/low priority)
- Code patterns extracted
- Testing insights
- Migration path

## 🎯 Navigation Guide

### By Role

**SDK User / Application Developer**:
1. Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
2. Read [SSE_STREAMING.md](./SSE_STREAMING.md) for streaming
3. Read [REST_API.md](./REST_API.md) for CRUD operations

**SDK Contributor / Maintainer**:
1. Read [ARCHITECTURE.md](./ARCHITECTURE.md)
2. Review [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md)
3. Check specific guides based on feature area

**Product Manager / Technical Lead**:
1. Start with [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md)
2. Review [OAUTH_CONNECTORS.md](./OAUTH_CONNECTORS.md) for feature planning
3. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for scaling considerations

### By Task

**Implementing SSE Streaming**:
→ [SSE_STREAMING.md](./SSE_STREAMING.md)

**Adding REST Endpoints**:
→ [REST_API.md](./REST_API.md)

**Planning OAuth Features**:
→ [OAUTH_CONNECTORS.md](./OAUTH_CONNECTORS.md)

**Understanding Architecture**:
→ [ARCHITECTURE.md](./ARCHITECTURE.md)

**Quick Code Lookup**:
→ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

**Planning Features**:
→ [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md)

## 🔍 Key Topics

### Protocol & API

- **Protocol Version**: 2.17-2.18
- **Total Endpoints**: 38+ (2 SSE + 24 REST + 11 Connectors + 1 Service Worker)
- **SSE Events**: query_progress, search_results, answer_chunk, final_response, error
- **Authentication**: Cookie-based session tokens

### Architecture

- **Layers**: Core → Shared → Transport → Domain → Client
- **Patterns**: Factory, Builder, Iterator, Strategy
- **Type Safety**: mypy strict mode, Protocol-based interfaces
- **Async**: asyncio-first, non-blocking I/O

### Features

**Currently Implemented**:
- ✅ SSE streaming (via `Conversation.ask_stream()`)
- ✅ Entry management (create entries via streaming)
- ✅ Retry with exponential backoff
- ✅ Type-safe Pydantic models

**Planned** (from knowledge integration):
- 🔄 REST API for threads (list, create, update, delete)
- 🔄 REST API for collections management
- 🔄 Entry forking and JSON Patch updates
- 🔄 Rate limiting improvements
- ⚠️ OAuth connectors (Google Drive, Notion, etc.)
- 📋 Service worker analysis (version detection)

## 🔗 External References

### RFCs & Specifications
- [Server-Sent Events (WHATWG HTML Living Standard)](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [SSE over HTTP/2 (RFC 8895)](https://www.rfc-editor.org/rfc/rfc8895.html)
- [RFC 6902 - JSON Patch](https://www.rfc-editor.org/rfc/rfc6902.html)
- [RFC 6749 - OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749.html)

### Related Projects
- [pplx-unofficial-sdk](https://github.com/pv-udpv/pplx-unofficial-sdk) - TypeScript SDK (Protocol 2.18)
- [Perplexity AI Docs](https://docs.perplexity.ai/) - Official documentation

## 📊 Documentation Stats

```
File                          Lines    Size    Topics
─────────────────────────────────────────────────────
QUICK_REFERENCE.md              221   6.1KB   Quick lookups
ARCHITECTURE.md                 388    11KB   System design
SSE_STREAMING.md                557    13KB   Streaming protocol
REST_API.md                     709    15KB   API reference
OAUTH_CONNECTORS.md             698    15KB   OAuth integration
KNOWLEDGE_INTEGRATION.md        505    13KB   Summary & roadmap
─────────────────────────────────────────────────────
TOTAL                         2,978    73KB   6 comprehensive guides
```

## 🚀 Getting Started

### New to pplx-sdk?

1. **Read**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (5 min)
2. **Try**: Run the quick start examples
3. **Deep Dive**: Pick specific guide based on your needs

### Contributing?

1. **Understand**: [ARCHITECTURE.md](./ARCHITECTURE.md) (15 min)
2. **Review**: [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md) (10 min)
3. **Implement**: Check roadmap and pick a task

### Planning Features?

1. **Survey**: [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md) (10 min)
2. **Detail**: Read relevant specific guide
3. **Plan**: Use implementation recommendations

## 📝 Documentation Principles

This documentation follows these principles:

1. **Actionable**: Every guide includes working code examples
2. **Cross-Referenced**: Easy navigation between related topics
3. **Dual Language**: Python and TypeScript examples where relevant
4. **Standards-Based**: References RFCs and specifications
5. **Future-Focused**: Includes roadmap and recommendations

## 🔄 Updates & Maintenance

**Last Updated**: 2024-02-08  
**Protocol Version**: 2.17-2.18  
**Source Integration**: @pv-udpv/pplx-unofficial-sdk, @pv-udpv/perplexity-ai-unofficial

To update this documentation:
1. Research latest protocol changes
2. Update relevant guide(s)
3. Update KNOWLEDGE_INTEGRATION.md comparison matrix
4. Update this index if adding new files

## 💡 Tips

- **Bookmark** [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for frequent lookups
- **Search** across all docs for specific topics (use grep/ctrl+F)
- **Follow** the implementation roadmap in [KNOWLEDGE_INTEGRATION.md](./KNOWLEDGE_INTEGRATION.md)
- **Reference** TypeScript examples for inspiration
- **Validate** protocol version before implementing features

---

**Maintained by**: pplx-sdk team  
**Questions?**: Open an issue on GitHub  
**Contribute**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
