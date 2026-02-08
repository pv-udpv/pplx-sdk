# Documentation Index

This directory contains comprehensive research and documentation for the pplx-sdk agentic system.

## 📚 Documents

### 1. [AGENTIC_SYSTEM_RESEARCH.md](./AGENTIC_SYSTEM_RESEARCH.md)

**Primary research document** covering:
- ✅ Latest merged PR #22 analysis (MCP servers, agent discovery, CI modernization)
- ✅ Dual-path agent architecture (GitHub Copilot + external runners)
- ✅ Skills & subagents overview (9 skills, 10 subagents, 9 task templates)
- ✅ Agent handoff workflows (new-feature, bug-fix, SSE, API-discovery)
- ✅ Testing with real issues (#8, #6, #11)
- ✅ Test results and recommendations

**Use this for:**
- Understanding the agentic system architecture
- Learning agent handoff patterns
- Planning multi-agent workflows
- Onboarding new contributors

### 2. [AGENT_HANDOFF_TESTS.md](./AGENT_HANDOFF_TESTS.md)

**Test scripts and scenarios** including:
- Test Scenario 1: Issue #8 (simple validation workflow)
- Test Scenario 2: Issue #6 (complex multi-phase workflow)
- Test Scenario 3: Issue #11 (epic multi-agent workflow)
- Python test scripts for automation
- Expected output examples
- Key observations and lessons learned

**Use this for:**
- Testing agent handoff workflows
- Validating agent coordination
- Debugging workflow issues
- Creating new test scenarios

### 3. [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md)

**Visual documentation** with Mermaid diagrams:
- Dual-path architecture overview
- Agent handoff sequence diagram
- Skill & subagent mapping
- Standard workflows visualization
- Layer architecture (core → shared → transport → domain → client)
- MCP server integration

**Use this for:**
- Visualizing system architecture
- Understanding agent relationships
- Documenting workflows
- Presentations and onboarding

## 🎯 Quick Start

### For GitHub Copilot Users

1. Read [AGENTIC_SYSTEM_RESEARCH.md](./AGENTIC_SYSTEM_RESEARCH.md) Part 2 (Dual-Path Architecture)
2. Review [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) for visual overview
3. Use `@agent` mentions in GitHub Copilot chat
4. Reference skills by name in prompts

**Example:**
```
@pplx-sdk-expert Review pplx_sdk/transport/http.py for architecture compliance
```

### For External Agent Runner Users

1. Read [AGENTIC_SYSTEM_RESEARCH.md](./AGENTIC_SYSTEM_RESEARCH.md) Part 3 (Skills & Subagents)
2. Load task templates from `tasks/*.json`
3. Chain tasks into workflows
4. Use [AGENT_HANDOFF_TESTS.md](./AGENT_HANDOFF_TESTS.md) for examples

**Example:**
```python
import json

# Load task template
with open("tasks/code-review.json") as f:
    task = json.load(f)

# Execute
result = agent.execute(task, inputs={"target": "pplx_sdk/transport/"})
```

### For Repository Maintainers

1. Review all three documents for comprehensive understanding
2. Use diagrams in README and PR descriptions
3. Reference test scenarios when planning work
4. Keep documentation in sync with code changes

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| MCP Servers | 6 (github-rw, perplexity_ai, deep-wiki, fetch, context7, llms-txt) |
| Skills | 9 (code-review, test-fix, scaffold, SSE, reverse-engineer, architecture, SPA, code-analysis, meta) |
| Subagents | 10 (orchestrator + 9 specialists) |
| Task Templates | 9 (matching skills + explore + full-workflow) |
| Open Issues | 11 (multiple ready for agent handoff) |
| CI Runtime | ~2-2.5 minutes (40% improvement from PR #22) |
| Test Cases | 3 (validated agent handoff workflows) |

## 🔗 Related Files

- **Main README:** [`../README.md`](../README.md) — Project overview
- **Agent Manifest:** [`../agent.json`](../agent.json) — Agent configuration
- **MCP Config:** [`../.copilot/mcp.json`](../.copilot/mcp.json) — MCP server configuration
- **Copilot Instructions:** [`../.github/copilot-instructions.md`](../.github/copilot-instructions.md) — Development guidelines
- **Skills:** [`../skills/`](../skills/) — Skill definitions (symlinked from `.agents/skills/`)
- **Subagents:** [`../.claude/agents/`](../.claude/agents/) — Subagent specifications
- **Tasks:** [`../tasks/`](../tasks/) — Task templates

## 🚀 Next Actions

Based on research findings:

1. **Close Issue #8** — `.github/copilot-instructions.md` complete (all criteria met)
2. **Finalize Issue #6** — remove deprecated `pplx_sdk.utils` shim and close refactor
3. **Break down Issue #11** — Split epic into phases matching agent workflow
4. **Add integration tests** — Automate agent handoff validation
5. **Update README** — Add agent handoff patterns from research

## 📝 Contributing

When updating these documents:

1. **Maintain consistency** — Keep all three documents in sync
2. **Update diagrams** — Regenerate Mermaid diagrams when architecture changes
3. **Add test scenarios** — Document new agent handoff patterns
4. **Version control** — Track document versions in git
5. **Link from main README** — Ensure discoverability

## 📅 Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-08 | Initial research and documentation |

---

**Research By:** GitHub Copilot Coding Agent  
**Repository:** [pv-udpv/pplx-sdk](https://github.com/pv-udpv/pplx-sdk)  
**Last Updated:** 2026-02-08 10:38:04 UTC
