"""Event type definitions for SSE streaming."""

from enum import Enum


class EventType(str, Enum):
    """SSE event types from Perplexity API."""

    QUERY_PROGRESS = "query_progress"
    SEARCH_RESULTS = "search_results"
    ANSWER_STARTED = "answer_started"
    ANSWER_CHUNK = "answer_chunk"
    FINAL_RESPONSE = "final_response"
    RELATED_QUESTIONS = "related_questions"
    ERROR = "error"
    BACKEND_UUID = "backend_uuid"
    SEARCH_FOCUS = "search_focus"
    QUERY_REPHRASED = "query_rephrased"
