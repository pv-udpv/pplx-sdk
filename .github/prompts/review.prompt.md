---
description: "Review code changes for pplx-sdk conventions"
name: "review"
argument-hint: "Describe what to review (e.g., 'transport layer changes')"
---

Review the specified code changes following pplx-sdk project standards:

## Checklist

1. **Type Safety**: All functions have complete type annotations. Run `mypy pplx_sdk/` mentally.
2. **Architecture Layers**: Verify imports respect `core → shared → transport/domain → client` dependency flow. No circular imports.
3. **Error Handling**: Custom exceptions from `pplx_sdk.core.exceptions` are used (not bare `Exception`). Exceptions are chained with `from exc`.
4. **Docstrings**: Google-style docstrings on all public classes and methods with Args, Returns, Raises sections.
5. **Testing**: Tests follow Arrange-Act-Assert pattern with descriptive names (`test_<module>_<behavior>`).
6. **Pydantic Models**: Domain models use Pydantic v2 BaseModel with `Field()` descriptions.
7. **Transport Protocol**: Transport implementations follow the `Transport` protocol from `pplx_sdk.core.protocols`.

## Output Format

For each file, provide:
- ✅ Passes check — or
- ❌ Issue found: description and suggested fix
