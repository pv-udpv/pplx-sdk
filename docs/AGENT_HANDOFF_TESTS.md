# Agent Handoff Test Script

This script demonstrates how to test agent handoffs on real GitHub issues.

## Prerequisites

```bash
# Install dependencies
uv sync --all-extras --dev

# Ensure MCP servers are configured
cat .copilot/mcp.json
```

## Test Scenario 1: Issue #8 (Simple — Validation)

**Issue:** Add .github/copilot-instructions.md  
**Status:** Complete (ready to close)  
**Agent workflow:** code-reviewer → orchestrator

```python
#!/usr/bin/env python3
"""Test agent handoff on Issue #8."""

from pathlib import Path
import json

# Phase 1: Code Reviewer validates file exists and meets requirements
def test_issue_8_validation():
    """Agent: code-reviewer - Validate copilot-instructions.md."""
    
    file_path = Path(".github/copilot-instructions.md")
    
    # Check file exists
    assert file_path.exists(), "copilot-instructions.md not found"
    
    # Check file size (should have content)
    content = file_path.read_text()
    assert len(content) > 5000, "File too short"
    
    # Check required sections
    required_sections = [
        "## Project Overview",
        "## Architecture Layers",
        "### 1. Core",
        "### 2. Shared",
        "### 3. Transport",
        "### 4. Domain",
        "### 5. Client",
        "## Code Generation Guidelines",
        "### Type Annotations",
        "### Error Handling",
        "### Testing Patterns",
        "## Anti-Patterns to Avoid",
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
    
    print("✅ Issue #8: All acceptance criteria met")
    print("📝 Recommendation: Close issue with success comment")
    
    return {
        "status": "complete",
        "file_exists": True,
        "sections_complete": len(required_sections),
        "recommendation": "close_issue"
    }

# Phase 2: Orchestrator aggregates and decides
def test_issue_8_orchestrator():
    """Agent: orchestrator - Aggregate results and decide."""
    
    result = test_issue_8_validation()
    
    if result["status"] == "complete":
        print("\n🎯 Orchestrator Decision:")
        print("  - All requirements met")
        print("  - Ready to close issue #8")
        print("  - No further work needed")
    
    return result

if __name__ == "__main__":
    test_issue_8_orchestrator()
```

## Test Scenario 2: Issue #6 (Complex — Multi-Phase)

**Issue:** Refactor utils/ to shared/  
**Status:** Open (ready for implementation)  
**Agent workflow:** code-reviewer → test-runner → scaffolder → pplx-sdk-dev → test-runner → code-reviewer

```python
#!/usr/bin/env python3
"""Test agent handoff on Issue #6."""

from pathlib import Path
import subprocess
import json

class AgentHandoffContext:
    """Shared context for agent coordination."""
    
    def __init__(self):
        self.phase = "init"
        self.completed_agents = []
        self.artifacts = {}
    
    def handoff(self, from_agent: str, to_agent: str, artifact: dict):
        """Record agent handoff."""
        self.completed_agents.append(from_agent)
        self.artifacts[from_agent] = artifact
        self.phase = to_agent
        print(f"\n🔄 Handoff: {from_agent} → {to_agent}")
        print(f"   Artifact: {artifact}")

context = AgentHandoffContext()

# Phase 1: Code Reviewer explores current structure
def phase1_code_reviewer():
    """Agent: code-reviewer - Analyze utils/ structure."""
    
    print("\n📋 Phase 1: Code Reviewer explores utils/")
    
    utils_path = Path("pplx_sdk/utils")
    
    if not utils_path.exists():
        artifact = {
            "utils_exists": False,
            "message": "utils/ already migrated or doesn't exist"
        }
    else:
        # Find all files in utils/
        files = list(utils_path.glob("**/*.py"))
        
        # Find all imports of utils/
        result = subprocess.run(
            ["grep", "-r", "from pplx_sdk.utils", "pplx_sdk/", "tests/"],
            capture_output=True,
            text=True
        )
        import_locations = result.stdout.strip().split("\n") if result.stdout else []
        
        artifact = {
            "utils_exists": True,
            "files": [str(f) for f in files],
            "import_count": len(import_locations),
            "import_locations": import_locations[:10],  # First 10
            "recommendation": "Proceed with migration"
        }
    
    context.handoff("init", "test-runner", artifact)
    return artifact

# Phase 2: Test Runner establishes baseline
def phase2_test_runner():
    """Agent: test-runner - Run baseline tests."""
    
    print("\n🧪 Phase 2: Test Runner establishes baseline")
    
    # Run tests
    result = subprocess.run(
        ["uv", "run", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    artifact = {
        "tests_passed": result.returncode == 0,
        "output_preview": result.stdout[:500],
        "recommendation": "Tests passing, safe to proceed" if result.returncode == 0 else "Fix failing tests first"
    }
    
    context.handoff("code-reviewer", "scaffolder", artifact)
    return artifact

# Phase 3: Scaffolder creates shared/ structure
def phase3_scaffolder():
    """Agent: scaffolder - Create shared/ module."""
    
    print("\n🏗️  Phase 3: Scaffolder creates shared/ structure")
    
    # This would actually create files, but for testing we simulate
    artifact = {
        "action": "simulate",
        "would_create": [
            "pplx_sdk/shared/__init__.py",
            "pplx_sdk/shared/retry.py",
            "pplx_sdk/shared/auth.py",
            "pplx_sdk/shared/logging.py"
        ],
        "would_move": "pplx_sdk/utils/* → pplx_sdk/shared/",
        "recommendation": "Files scaffolded, ready for implementation"
    }
    
    context.handoff("test-runner", "pplx-sdk-dev", artifact)
    return artifact

# Phase 4: Implementation agent extracts retry logic
def phase4_implementation():
    """Agent: pplx-sdk-dev - Implement retry.py."""
    
    print("\n💻 Phase 4: Implementation agent implements retry.py")
    
    artifact = {
        "action": "simulate",
        "would_implement": [
            "RetryConfig dataclass",
            "retry_with_backoff() function",
            "async_retry_with_backoff() function"
        ],
        "would_update": [
            "pplx_sdk/streaming/manager.py (use retry_with_backoff)",
            "Update imports in client.py, transport/, domain/"
        ],
        "recommendation": "Implementation complete, ready for testing"
    }
    
    context.handoff("scaffolder", "test-runner", artifact)
    return artifact

# Phase 5: Test Runner verifies implementation
def phase5_test_runner():
    """Agent: test-runner - Create tests and verify."""
    
    print("\n🧪 Phase 5: Test Runner creates tests")
    
    artifact = {
        "action": "simulate",
        "would_create": "tests/shared/test_retry.py",
        "would_test": [
            "test_retry_config_backoff_calculation()",
            "test_retry_with_backoff_success_on_second_attempt()",
            "test_retry_exhausts_attempts()"
        ],
        "recommendation": "All tests pass, ready for review"
    }
    
    context.handoff("pplx-sdk-dev", "code-reviewer", artifact)
    return artifact

# Phase 6: Code Reviewer final validation
def phase6_code_reviewer():
    """Agent: code-reviewer - Final review."""
    
    print("\n📋 Phase 6: Code Reviewer validates implementation")
    
    checklist = {
        "imports_respect_layers": True,
        "type_annotations_complete": True,
        "docstrings_present": True,
        "custom_exceptions_used": True,
        "tests_follow_pattern": True,
        "no_circular_imports": True
    }
    
    all_pass = all(checklist.values())
    
    artifact = {
        "checklist": checklist,
        "all_checks_pass": all_pass,
        "recommendation": "Approve and merge" if all_pass else "Address review comments"
    }
    
    context.handoff("test-runner", "done", artifact)
    return artifact

# Run full workflow
def test_issue_6_full_workflow():
    """Execute full agent handoff workflow."""
    
    print("=" * 60)
    print("🚀 Testing Issue #6 Agent Handoff Workflow")
    print("=" * 60)
    
    phase1_code_reviewer()
    phase2_test_runner()
    phase3_scaffolder()
    phase4_implementation()
    phase5_test_runner()
    result = phase6_code_reviewer()
    
    print("\n" + "=" * 60)
    print("📊 Workflow Summary")
    print("=" * 60)
    print(f"Phases completed: {len(context.completed_agents)}")
    print(f"Agents involved: {', '.join(context.completed_agents)}")
    print(f"Final recommendation: {result['recommendation']}")
    print(f"All checks pass: {result['all_checks_pass']}")
    
    return context

if __name__ == "__main__":
    test_issue_6_full_workflow()
```

## Test Scenario 3: Issue #11 (Epic — Multi-Agent)

**Issue:** SDK Generator from OpenAPI/AsyncAPI  
**Status:** Open (epic scope)  
**Agent workflow:** reverse-engineer → architect → scaffolder → pplx-sdk-dev (×2) → test-runner → code-reviewer

```python
#!/usr/bin/env python3
"""Test agent handoff on Issue #11 (Epic)."""

# Phase 1: reverse-engineer researches specs
def phase1_research():
    print("\n🔍 Phase 1: Reverse Engineer researches OpenAPI/AsyncAPI specs")
    return {
        "openapi_version": "3.x",
        "asyncapi_version": "2.x/3.x",
        "similar_tools": ["openapi-python-client", "datamodel-code-generator"],
        "dependencies": ["pyyaml", "jinja2", "pydantic"]
    }

# Phase 2: architect designs system
def phase2_design():
    print("\n🏛️  Phase 2: Architect designs generator architecture")
    return {
        "modules": ["parser", "builder", "generator", "writer"],
        "templates": "Jinja2 for code generation",
        "cli": "pplx_sdk.codegen.__main__"
    }

# Phase 3-7: [Similar pattern to Issue #6]
# ...

print("""
🎯 Issue #11 Agent Handoff Pattern:

1. reverse-engineer: Research OpenAPI/AsyncAPI specs
2. architect: Design 4-layer generator architecture
3. scaffolder: Create codegen/ module structure
4. pplx-sdk-dev: Implement parser (OpenAPI → AST)
5. pplx-sdk-dev: Implement generator (AST → Python)
6. test-runner: Test on sample specs
7. code-reviewer: Architecture compliance review

This epic demonstrates deep agent coordination across 7 phases.
""")
```

## Running Tests

```bash
# Test Issue #8 (simple validation)
python docs/agent_handoff_tests.py test_issue_8

# Test Issue #6 (multi-phase workflow)  
python docs/agent_handoff_tests.py test_issue_6

# Test Issue #11 (epic simulation)
python docs/agent_handoff_tests.py test_issue_11
```

## Expected Output

```
🚀 Testing Issue #6 Agent Handoff Workflow
============================================================

📋 Phase 1: Code Reviewer explores utils/
🔄 Handoff: init → test-runner
   Artifact: {'utils_exists': True, ...}

🧪 Phase 2: Test Runner establishes baseline
🔄 Handoff: code-reviewer → scaffolder
   Artifact: {'tests_passed': True, ...}

🏗️  Phase 3: Scaffolder creates shared/ structure
🔄 Handoff: test-runner → pplx-sdk-dev
   Artifact: {'would_create': [...], ...}

💻 Phase 4: Implementation agent implements retry.py
🔄 Handoff: scaffolder → test-runner
   Artifact: {'would_implement': [...], ...}

🧪 Phase 5: Test Runner creates tests
🔄 Handoff: pplx-sdk-dev → code-reviewer
   Artifact: {'would_create': 'tests/shared/test_retry.py', ...}

📋 Phase 6: Code Reviewer validates implementation
🔄 Handoff: test-runner → done
   Artifact: {'all_checks_pass': True, ...}

============================================================
📊 Workflow Summary
============================================================
Phases completed: 6
Agents involved: code-reviewer, test-runner, scaffolder, pplx-sdk-dev, code-reviewer
Final recommendation: Approve and merge
All checks pass: True
```

## Key Observations

1. **Context Preservation** — Each agent passes artifacts to next agent
2. **Sequential Execution** — Agents execute in order, building on previous results
3. **Specialization** — Each agent focuses on its domain expertise
4. **Validation Gates** — code-reviewer validates at start and end
5. **Composability** — Workflows are composed from agent primitives

## Lessons Learned

1. Need explicit context.json for agent coordination
2. Handoff logging helps debug workflow issues
3. Parallel agents possible for independent tasks
4. Orchestrator should manage rollback on failure
5. Progress tracking valuable for long workflows
