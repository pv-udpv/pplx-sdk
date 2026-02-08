"""Domain models for Perplexity API entities.

This module contains Pydantic models representing core entities:
- Thread: Conversation threads with metadata
- Entry: Question-answer pairs within threads
- MessageChunk: Streaming SSE events
- Block: Structured answer blocks
- Source: Citation sources
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class StreamStatus(StrEnum):
    """Status values for streaming events."""

    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ANSWER_STARTED = "answer_started"
    ANSWER_COMPLETED = "answer_completed"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    RESUMING = "resuming"


class ThreadAccess(StrEnum):
    """Access level for threads."""

    PRIVATE = "private"
    ORG = "org"
    PUBLIC = "public"


class SourceType(StrEnum):
    """Type of citation source."""

    WEB = "web"
    ACADEMIC = "academic"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    WIKIPEDIA = "wikipedia"


class Block(BaseModel):
    """Structured answer block within an entry."""

    type: str = Field(description="Block type (text, code, list, etc.)")
    content: str = Field(description="Block content")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


class Source(BaseModel):
    """Citation source for an entry."""

    type: SourceType = Field(description="Source type")
    url: str = Field(description="Source URL")
    title: str | None = Field(default=None, description="Source title")
    snippet: str | None = Field(default=None, description="Text snippet")
    favicon: str | None = Field(default=None, description="Favicon URL")
    position: int | None = Field(default=None, description="Position in results")


class Thread(BaseModel):
    """Conversation thread entity.

    Represents a conversation thread with multiple entries.
    """

    context_uuid: str = Field(description="Unique thread identifier")
    title: str | None = Field(default=None, description="Thread title")
    slug: str = Field(description="URL-friendly slug")
    access: ThreadAccess = Field(default=ThreadAccess.PRIVATE, description="Access level")
    fork_count: int = Field(default=0, description="Number of forks")
    like_count: int = Field(default=0, description="Number of likes")
    view_count: int = Field(default=0, description="Number of views")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class Entry(BaseModel):
    """Question-answer entry within a thread.

    Represents a single Q&A exchange with sources and structured content.
    """

    backend_uuid: str = Field(description="Server-generated entry ID")
    frontend_uuid: str = Field(description="Client-generated entry ID")
    context_uuid: str = Field(description="Parent thread UUID")
    status: StreamStatus = Field(description="Entry status")
    text_completed: bool = Field(default=False, description="Whether text generation is complete")
    blocks: list[Block] = Field(default_factory=list, description="Structured answer blocks")
    sources: list[Source] = Field(default_factory=list, description="Citation sources")
    query: str | None = Field(default=None, description="Original query")
    display_model: str | None = Field(default=None, description="Model used for generation")
    parent_entry_uuid: str | None = Field(
        default=None, description="Parent entry for threaded queries"
    )
    cursor: str | None = Field(default=None, description="Resume cursor for reconnection")


class MessageChunk(BaseModel):
    """SSE event chunk from streaming response.

    Represents a single event in the SSE stream.
    """

    type: str = Field(description="Event type (query_progress, answer_chunk, etc.)")
    status: str | None = Field(default=None, description="Status value")
    data: dict[str, Any] = Field(default_factory=dict, description="Event-specific payload")
    backend_uuid: str | None = Field(default=None, description="Entry backend UUID")
    context_uuid: str | None = Field(default=None, description="Thread context UUID")
    text: str | None = Field(default=None, description="Text content for answer chunks")
    cursor: str | None = Field(default=None, description="Resume cursor")
    reconnectable: bool = Field(default=False, description="Whether stream can be reconnected")
