"""Common type aliases."""

from __future__ import annotations

from typing import Any, Dict, Literal

from typing_extensions import TypeAlias

# HTTP types
Headers: TypeAlias = Dict[str, str]
QueryParams: TypeAlias = Dict[str, Any]
JSONData: TypeAlias = Dict[str, Any]

# Perplexity-specific types
Mode: TypeAlias = Literal["concise", "research", "creative"]
SearchFocus: TypeAlias = Literal["internet", "scholar", "youtube", "reddit", "all"]
ModelPreference: TypeAlias = Literal[
    "pplx-7b-online",
    "pplx-70b-chat",
    "pplx-70b-deep",
    "claude-3-opus",
    "gpt-4-turbo",
]

# Entry status
EntryStatus: TypeAlias = Literal["pending", "completed", "failed", "resuming"]

# SSE event types
SSEEventType: TypeAlias = Literal[
    "query_progress",
    "search_results",
    "answer_started",
    "answer_chunk",
    "final_response",
    "related_questions",
    "error",
]
