"""Common type aliases."""

from __future__ import annotations

from typing import Any, Literal

# HTTP types
type Headers = dict[str, str]
type QueryParams = dict[str, Any]
type JSONData = dict[str, Any]

# Perplexity-specific types
type Mode = Literal["concise", "research", "creative"]
type SearchFocus = Literal["internet", "scholar", "youtube", "reddit", "all"]
type ModelPreference = Literal[
    "pplx-7b-online",
    "pplx-70b-chat",
    "pplx-70b-deep",
    "claude-3-opus",
    "gpt-4-turbo",
]

# Entry status
type EntryStatus = Literal["pending", "completed", "failed", "resuming"]

# SSE event types
type SSEEventType = Literal[
    "query_progress",
    "search_results",
    "answer_started",
    "answer_chunk",
    "final_response",
    "related_questions",
    "error",
]
