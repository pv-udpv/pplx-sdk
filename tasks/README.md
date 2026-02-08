# Task Templates

Task templates wrap skills into executable actions for **pplx-sdk** and other
external agent runners (Cline, obra/superpowers, custom MCP hosts).

> **GitHub Copilot Coding Agent** does not use this directory.
> It reads only the prompt template (`.github/copilot-instructions.md`)
> and MCP servers (`.copilot/mcp.json`). Skill behaviors are embedded
> directly in the prompt for Copilot.

## Architecture

```
┌──────────────────────────┐
│  GitHub Coding Agent UI  │  ← prompt + MCP only
│  .github/copilot-        │
│    instructions.md       │
│  .copilot/mcp.json       │
└──────────┬───────────────┘
           │ (capabilities via MCP)
           ▼
┌──────────────────────────┐
│     MCP Servers          │  ← shared capability layer
│  (GitHub, fetch, etc.)   │
└──────────┬───────────────┘
           │ (also used by)
           ▼
┌──────────────────────────┐
│  pplx-sdk / Cline runner │  ← tasks + skills + agent.json
│  tasks/*.json             │
│  skills/                  │
│  agent.json               │
└──────────────────────────┘
```

## How Tasks Work

Each `.json` file defines an executable action with:

| Field | Purpose |
|-------|---------|
| `agent_type` | Which agent handles the task (`explore`, `implement`, `review`, `test`, `analyze`) |
| `skill` | Which skill provides the behavior |
| `prompt` | What the agent should do |
| `inputs` | Dynamic values the runner fills in |
| `outputs` | What the task produces |

## Usage

External agent runners load a task template and execute it:

```python
import json

with open("tasks/code-review.json") as f:
    task = json.load(f)

# Runner fills in the dynamic inputs
task["inputs"]["target"] = "pplx_sdk/transport/http.py"

# Runner dispatches to the appropriate agent_type
runner.execute(task)
```

## Available Tasks

| Task | Skill | Agent Type | Purpose |
|------|-------|------------|---------|
| `code-review.json` | code-review | review | Review code against architecture conventions |
| `test-fix.json` | test-fix | test | Diagnose and fix failing tests |
| `scaffold-module.json` | scaffold-module | implement | Create new modules per layered architecture |
| `sse-streaming.json` | sse-streaming | implement | Implement SSE streaming features |
| `reverse-engineer.json` | reverse-engineer | explore | Discover undocumented API endpoints |
| `architecture.json` | architecture | analyze | Generate architecture diagrams |
| `code-analysis.json` | code-analysis | analyze | AST parsing and dependency analysis |
| `explore.json` | pplx-sdk-dev | explore | General codebase exploration |
| `full-workflow.json` | pplx-sdk-dev | orchestrate | End-to-end feature workflow |
