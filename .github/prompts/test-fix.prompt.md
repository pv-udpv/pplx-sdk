---
description: "Fix failing tests in pplx-sdk"
name: "test-fix"
argument-hint: "Paste the test failure output or describe which tests fail"
---

Fix the failing tests following pplx-sdk conventions:

## Steps

1. **Read the failure output** carefully — identify the root cause (assertion error, import error, missing mock, etc.).
2. **Check the source code** that the test exercises — the fix may be in the source, not the test.
3. **Follow existing patterns**: Look at passing tests in the same file for mock setup and assertion style.
4. **Preserve test intent**: Don't weaken assertions to make tests pass. Fix the underlying issue.

## Project-Specific Notes

- Use `pytest-httpx` (`HTTPXMock`) for mocking HTTP requests in transport tests.
- Use fixtures from `tests/conftest.py` for common test data (`mock_auth_token`, `mock_context_uuid`, etc.).
- Exception tests should verify the exception hierarchy: `AuthenticationError → TransportError → PerplexitySDKError`.
- SSE parsing tests should verify the full event lifecycle: `event: type\ndata: {json}\n\n`.

## Output

Provide the minimal fix with an explanation of what was wrong and why the fix is correct.
