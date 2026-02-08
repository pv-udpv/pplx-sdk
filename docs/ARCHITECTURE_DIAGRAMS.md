# Agent Handoff Architecture Diagrams

## 1. Dual-Path Architecture

```mermaid
graph TB
    subgraph "Path 1: GitHub Copilot"
        A[.github/copilot-instructions.md]
        B[.copilot/mcp.json]
        A --> C[Embedded Skill Behaviors]
        B --> D[MCP Configuration]
    end
    
    subgraph "Shared MCP Layer"
        E[github-rw HTTP MCP]
        F[perplexity_ai HTTP MCP]
        G[deep-wiki npx MCP]
        H[fetch npx MCP]
        I[context7 npx MCP]
        J[llms-txt npx MCP]
    end
    
    subgraph "Path 2: External Runners"
        K[agent.json]
        L[tasks/*.json]
        M[skills/*/SKILL.md]
        N[.claude/agents/*.md]
    end
    
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    C --> J
    
    K --> E
    K --> F
    K --> G
    K --> H
    K --> I
    K --> J
    
    L --> M
    M --> N
    
    style A fill:#4CAF50
    style K fill:#2196F3
    style E fill:#FF9800
    style F fill:#FF9800
    style G fill:#FF9800
    style H fill:#FF9800
    style I fill:#FF9800
    style J fill:#FF9800
```

## 2. Agent Handoff Workflow (Issue #6 Example)

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant CR as Code Reviewer
    participant TR as Test Runner
    participant S as Scaffolder
    participant I as Implementation
    
    O->>CR: Phase 1: Explore utils/ structure
    CR->>CR: Find files, imports, dependencies
    CR-->>O: Artifact: {files: [...], imports: [...]}
    
    O->>TR: Phase 2: Run baseline tests
    TR->>TR: pytest tests/ -v
    TR-->>O: Artifact: {tests_passed: true}
    
    O->>S: Phase 3: Create shared/ structure
    S->>S: Create shared/, retry.py, __init__.py
    S-->>O: Artifact: {created: [...]}
    
    O->>I: Phase 4: Implement retry logic
    I->>I: Extract from StreamManager, update imports
    I-->>O: Artifact: {implemented: [...]}
    
    O->>TR: Phase 5: Test implementation
    TR->>TR: Create test_retry.py, run all tests
    TR-->>O: Artifact: {tests_passed: true}
    
    O->>CR: Phase 6: Final review
    CR->>CR: Check layers, types, docs
    CR-->>O: Artifact: {approved: true}
    
    O->>O: ✅ Workflow Complete
```

## 3. Skill & Subagent Mapping

```mermaid
graph LR
    subgraph "Skills (SKILL.md)"
        S1[code-review]
        S2[test-fix]
        S3[scaffold-module]
        S4[sse-streaming]
        S5[reverse-engineer]
        S6[architecture]
        S7[spa-reverse-engineer]
        S8[code-analysis]
        S9[pplx-sdk-dev]
    end
    
    subgraph "Subagents (.claude/agents/)"
        A1[code-reviewer.md]
        A2[test-runner.md]
        A3[scaffolder.md]
        A4[sse-expert.md]
        A5[reverse-engineer.md]
        A6[architect.md]
        A7[spa-expert.md]
        A8[codegraph.md]
        A9[orchestrator.md]
    end
    
    subgraph "Task Templates (tasks/)"
        T1[code-review.json]
        T2[test-fix.json]
        T3[scaffold-module.json]
        T4[sse-streaming.json]
        T5[reverse-engineer.json]
        T6[architecture.json]
        T7[code-analysis.json]
    end
    
    S1 --> A1
    S1 --> T1
    
    S2 --> A2
    S2 --> T2
    
    S3 --> A3
    S3 --> T3
    
    S4 --> A4
    S4 --> T4
    
    S5 --> A5
    S5 --> T5
    
    S6 --> A6
    S6 --> T6
    
    S7 --> A7
    
    S8 --> A8
    S8 --> T7
    
    S9 --> A9
    
    style S1 fill:#4CAF50
    style S2 fill:#4CAF50
    style S3 fill:#4CAF50
    style A1 fill:#2196F3
    style A2 fill:#2196F3
    style A3 fill:#2196F3
    style T1 fill:#FF9800
    style T2 fill:#FF9800
    style T3 fill:#FF9800
```

## 4. Standard Workflows

```mermaid
graph TD
    subgraph "New Feature"
        NF1[plan] --> NF2[explore]
        NF2 --> NF3[research]
        NF3 --> NF4[scaffold]
        NF4 --> NF5[implement]
        NF5 --> NF6[test]
        NF6 --> NF7[review]
        NF7 --> NF8[verify]
    end
    
    subgraph "Bug Fix"
        BF1[reproduce] --> BF2[research]
        BF2 --> BF3[diagnose]
        BF3 --> BF4[fix]
        BF4 --> BF5[verify]
    end
    
    subgraph "SSE Streaming"
        SSE1[research] --> SSE2[implement]
        SSE2 --> SSE3[test]
        SSE3 --> SSE4[review]
    end
    
    subgraph "API Discovery"
        API1[capture] --> API2[research]
        API2 --> API3[document]
        API3 --> API4[scaffold]
        API4 --> API5[implement]
        API5 --> API6[test]
        API6 --> API7[review]
    end
    
    style NF1 fill:#4CAF50
    style BF1 fill:#2196F3
    style SSE1 fill:#FF9800
    style API1 fill:#9C27B0
```

## 5. Layer Architecture

```mermaid
graph BT
    subgraph "Layer 5: Client"
        L5[client.py<br/>PerplexityClient<br/>Conversation]
    end
    
    subgraph "Layer 4: Domain"
        L4A[threads.py<br/>ThreadService]
        L4B[entries.py<br/>EntryService]
        L4C[collections.py<br/>CollectionService]
    end
    
    subgraph "Layer 3: Transport"
        L3A[http.py<br/>HttpTransport]
        L3B[sse.py<br/>SSETransport]
    end
    
    subgraph "Layer 2: Shared"
        L2A[retry.py<br/>RetryConfig]
        L2B[auth.py<br/>extract_token]
        L2C[logging.py<br/>get_logger]
    end
    
    subgraph "Layer 1: Core"
        L1A[protocols.py<br/>Transport]
        L1B[types.py<br/>Headers, JSONData]
        L1C[exceptions.py<br/>TransportError]
    end
    
    L5 --> L4A
    L5 --> L4B
    L5 --> L4C
    
    L4A --> L3A
    L4B --> L3B
    
    L3A --> L2A
    L3A --> L2B
    L3B --> L2A
    
    L2A --> L1A
    L2A --> L1C
    L2B --> L1A
    
    style L5 fill:#4CAF50
    style L4A fill:#2196F3
    style L3A fill:#FF9800
    style L2A fill:#9C27B0
    style L1A fill:#F44336
```

## 6. MCP Server Integration

```mermaid
graph TB
    subgraph "Agents"
        A1[GitHub Copilot]
        A2[External Runners]
    end
    
    subgraph "MCP Protocol Layer"
        M[MCP JSON-RPC]
    end
    
    subgraph "HTTP MCP Servers"
        H1[github-rw<br/>api.githubcopilot.com]
        H2[perplexity_ai<br/>api.perplexity.ai]
    end
    
    subgraph "NPX MCP Servers"
        N1[deep-wiki<br/>mcp-deepwiki]
        N2[fetch<br/>@anthropic-ai/mcp-fetch]
        N3[context7<br/>@upstash/context7-mcp]
        N4[llms-txt<br/>@mcp-get-community/server-llm-txt]
    end
    
    A1 --> M
    A2 --> M
    
    M --> H1
    M --> H2
    M --> N1
    M --> N2
    M --> N3
    M --> N4
    
    H1 --> GH[GitHub API]
    H2 --> PP[Perplexity API]
    N1 --> WK[Wikipedia]
    N2 --> WEB[Web Content]
    N3 --> DOC[Documentation]
    N4 --> LLM[LLM Docs]
    
    style A1 fill:#4CAF50
    style A2 fill:#2196F3
    style M fill:#FF9800
    style H1 fill:#9C27B0
    style H2 fill:#9C27B0
    style N1 fill:#00BCD4
    style N2 fill:#00BCD4
    style N3 fill:#00BCD4
    style N4 fill:#00BCD4
```

## Legend

- 🟢 Green: GitHub Copilot / Entry points
- 🔵 Blue: External runners / Subagents
- 🟠 Orange: MCP servers / Transport layer
- 🟣 Purple: Shared utilities / HTTP MCP
- 🔴 Red: Core protocols / Foundation
- 🔷 Cyan: NPX MCP servers

## Usage in Documentation

These diagrams can be:
1. Embedded in README.md
2. Linked from agent.json
3. Used in onboarding docs
4. Referenced in PR descriptions
5. Displayed in architecture reviews
