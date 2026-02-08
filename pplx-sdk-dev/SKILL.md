---
name: pplx-sdk-dev
description: Meta-skill for pplx-sdk development. Orchestrates code review, testing, scaffolding, SSE streaming, and Python best practices into a unified workflow. Use for any development task on this project.
context: fork
agent: orchestrator
---

# pplx-sdk Development Meta-Skill

This meta-skill orchestrates all project-specific and community skills for pplx-sdk development. Activate this skill for any development task — it coordinates the right sub-skills automatically.

## When to use

Use this skill for **any** development task on the pplx-sdk project: implementing features, fixing bugs, reviewing code, writing tests, or scaffolding new modules.

## Subagent Architecture

Each skill delegates to a specialist subagent via `context: fork`. Subagents run in isolated context windows with restricted tool access.

```
┌─────────────────────────────────────────────┐
│              orchestrator                   │
│  (meta-orchestrator, delegates subtasks)    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ code-reviewer │  │ test-runner   │        │
│  │ (read-only)   │  │ (run & fix)   │        │
│  │ view,grep,    │  │ bash,view,    │        │
│  │ glob,bash     │  │ edit,grep     │        │
│  └──────────────┘  └──────────────┘        │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ scaffolder    │  │ sse-expert    │        │
│  │ (create new)  │  │ (streaming)   │        │
│  │ view,edit,    │  │ view,edit,    │        │
│  │ bash,grep     │  │ bash,grep     │        │
│  └──────────────┘  └──────────────┘        │
│                                             │
│  ┌────────────────────────────────┐        │
│  │ reverse-engineer               │        │
│  │ (API discovery & traffic       │        │
│  │  analysis, schema decoding)    │        │
│  │ view,edit,bash,grep,glob       │        │
│  └────────────────────────────────┘        │
│                                             │
└─────────────────────────────────────────────┘
```

### Subagent Definitions (`.claude/agents/`)

| Subagent | Role | Tools | Isolation |
|----------|------|-------|-----------|
| `orchestrator` | Decomposes tasks, coordinates others | view, bash, grep, glob | fork |
| `code-reviewer` | Read-only architecture review | view, grep, glob, bash | fork |
| `test-runner` | Run tests, diagnose, fix failures | bash, view, edit, grep, glob | fork |
| `scaffolder` | Create new modules and files | view, edit, bash, grep, glob | fork |
| `sse-expert` | SSE streaming implementation | view, edit, bash, grep, glob | fork |
| `reverse-engineer` | API discovery, traffic analysis | view, edit, bash, grep, glob | fork |

## Skill Dependencies

This meta-skill composes the following skills. Apply them in the order shown based on the task type.

### Project-Specific Skills (repo root)

| Skill | Path | Subagent | Purpose |
|-------|------|----------|---------|
| `code-review` | `code-review/SKILL.md` | `code-reviewer` | Architecture compliance and conventions |
| `test-fix` | `test-fix/SKILL.md` | `test-runner` | Diagnose and fix failing tests |
| `scaffold-module` | `scaffold-module/SKILL.md` | `scaffolder` | Create new modules per layered architecture |
| `sse-streaming` | `sse-streaming/SKILL.md` | `sse-expert` | SSE protocol and streaming patterns |
| `reverse-engineer` | `reverse-engineer/SKILL.md` | `reverse-engineer` | API discovery from browser traffic |

### Community Skills (installed via `npx skills`)

| Skill | Source | Purpose |
|-------|--------|---------|
| `python-testing-patterns` | `wshobson/agents` | pytest patterns, fixtures, mocking |
| `python-type-safety` | `wshobson/agents` | Type annotations, mypy strict mode |
| `python-error-handling` | `wshobson/agents` | Exception hierarchies, error patterns |
| `python-design-patterns` | `wshobson/agents` | Protocol pattern, DI, factory |
| `api-design-principles` | `wshobson/agents` | REST API design, endpoint conventions |
| `async-python-patterns` | `wshobson/agents` | async/await, concurrency patterns |

## Workflow: New Feature

```
[plan] → [explore] → [implement] → [test] → [review] → [done]
```

1. **Plan** — `orchestrator` decomposes the task, identifies target layer
2. **Explore** — `code-reviewer` (read-only fork) analyzes existing code
3. **Scaffold** — `scaffolder` (fork) creates files from templates
4. **Implement** — `sse-expert` or `scaffolder` (fork) writes the code
5. **Test** — `test-runner` (fork) runs pytest, fixes failures
6. **Review** — `code-reviewer` (fork) validates architecture compliance
7. **Verify** — `ruff check --fix . && ruff format . && mypy pplx_sdk/ && pytest -v`

## Workflow: Bug Fix

1. **Reproduce** — `test-runner` (fork) runs failing test with `-v`
2. **Diagnose** — `test-runner` reads traceback, identifies root cause
3. **Fix** — `test-runner` edits source/test, applies `python-error-handling` patterns
4. **Verify** — `test-runner` runs full suite

## Workflow: SSE/Streaming Work

1. **Understand** — `sse-expert` (fork) reviews protocol and existing transport code
2. **Implement** — `sse-expert` writes streaming code, applies `async-python-patterns`
3. **Test** — `test-runner` (fork) runs tests with mock SSE responses
4. **Review** — `code-reviewer` (fork) validates transport layer compliance

## Workflow: API Discovery (Reverse Engineering)

```
[capture] → [decode] → [document] → [scaffold] → [test] → [review]
```

1. **Capture** — `reverse-engineer` (fork) analyzes cURL/traffic from perplexity.ai DevTools
2. **Decode** — `reverse-engineer` extracts endpoint URL, auth, payload schema, response format
3. **Document** — `reverse-engineer` writes endpoint documentation with field types and examples
4. **Scaffold** — `scaffolder` (fork) creates Pydantic models and service methods from schema
5. **Implement** — `sse-expert` or `scaffolder` implements transport and domain code
6. **Test** — `test-runner` (fork) validates with mock responses matching discovered schemas
7. **Review** — `code-reviewer` (fork) ensures architecture compliance

## Workflow: API Endpoint

1. **Design** — `code-reviewer` reviews against `api-design-principles`
2. **Implement** — `scaffolder` (fork) creates FastAPI endpoint
3. **Test** — `test-runner` (fork) validates with pytest-httpx mocks

## Project Quick Reference

```bash
# Install dependencies
pip install -e ".[dev]"

# Install/update community skills
npx skills add wshobson/agents --skill python-testing-patterns --skill python-type-safety --skill python-error-handling --skill python-design-patterns --skill api-design-principles --skill async-python-patterns --agent github-copilot -y

# Lint, format, type-check, test
ruff check --fix . && ruff format .
mypy pplx_sdk/ --ignore-missing-imports
pytest tests/ -v --cov=pplx_sdk

# Manage skills
npx skills list          # Show installed skills
npx skills check         # Check for updates
npx skills update        # Update all skills
```

## Architecture Invariants

These rules must **never** be violated regardless of which sub-skill is active:

1. **Layer dependencies**: `core/ → shared/ → transport/ → domain/ → client.py` (never reverse)
2. **Exception hierarchy**: All errors extend `PerplexitySDKError`
3. **Type annotations**: 100% coverage, `from __future__ import annotations`
4. **Google docstrings**: On all public APIs
5. **Protocol pattern**: Use `typing.Protocol`, never ABC
