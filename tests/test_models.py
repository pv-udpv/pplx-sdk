"""Tests for domain models."""

from pplx_sdk.domain.models import (
    Block,
    Entry,
    MessageChunk,
    Source,
    SourceType,
    StreamStatus,
    Thread,
    ThreadAccess,
)


def test_thread_creation() -> None:
    """Test Thread model creation."""
    thread = Thread(
        context_uuid="test-uuid-123",
        title="Test Thread",
        slug="test-thread",
        access=ThreadAccess.PRIVATE,
    )

    assert thread.context_uuid == "test-uuid-123"
    assert thread.title == "Test Thread"
    assert thread.slug == "test-thread"
    assert thread.access == ThreadAccess.PRIVATE
    assert thread.fork_count == 0
    assert thread.like_count == 0


def test_block_creation() -> None:
    """Test Block model creation."""
    block = Block(
        type="text",
        content="This is a test block",
        metadata={"key": "value"},
    )

    assert block.type == "text"
    assert block.content == "This is a test block"
    assert block.metadata == {"key": "value"}


def test_source_creation() -> None:
    """Test Source model creation."""
    source = Source(
        type=SourceType.WEB,
        url="https://example.com",
        title="Example Page",
        snippet="This is an example",
    )

    assert source.type == SourceType.WEB
    assert source.url == "https://example.com"
    assert source.title == "Example Page"
    assert source.snippet == "This is an example"


def test_entry_creation() -> None:
    """Test Entry model creation."""
    entry = Entry(
        backend_uuid="backend-uuid-123",
        frontend_uuid="frontend-uuid-456",
        context_uuid="context-uuid-789",
        status=StreamStatus.COMPLETED,
        text_completed=True,
        blocks=[
            Block(type="text", content="Answer text"),
        ],
        sources=[
            Source(type=SourceType.WEB, url="https://example.com"),
        ],
    )

    assert entry.backend_uuid == "backend-uuid-123"
    assert entry.frontend_uuid == "frontend-uuid-456"
    assert entry.context_uuid == "context-uuid-789"
    assert entry.status == StreamStatus.COMPLETED
    assert entry.text_completed is True
    assert len(entry.blocks) == 1
    assert len(entry.sources) == 1


def test_message_chunk_creation() -> None:
    """Test MessageChunk model creation."""
    chunk = MessageChunk(
        type="answer_chunk",
        status="completed",
        data={"key": "value"},
        backend_uuid="backend-uuid",
        context_uuid="context-uuid",
        text="Test text",
        cursor="cursor-123",
        reconnectable=True,
    )

    assert chunk.type == "answer_chunk"
    assert chunk.status == "completed"
    assert chunk.data == {"key": "value"}
    assert chunk.backend_uuid == "backend-uuid"
    assert chunk.text == "Test text"
    assert chunk.cursor == "cursor-123"
    assert chunk.reconnectable is True


def test_stream_status_enum() -> None:
    """Test StreamStatus enum values."""
    assert StreamStatus.PENDING == "pending"
    assert StreamStatus.COMPLETED == "completed"
    assert StreamStatus.FAILED == "failed"
    assert StreamStatus.SEARCH_STARTED == "search_started"


def test_thread_access_enum() -> None:
    """Test ThreadAccess enum values."""
    assert ThreadAccess.PRIVATE == "private"
    assert ThreadAccess.ORG == "org"
    assert ThreadAccess.PUBLIC == "public"


def test_source_type_enum() -> None:
    """Test SourceType enum values."""
    assert SourceType.WEB == "web"
    assert SourceType.ACADEMIC == "academic"
    assert SourceType.REDDIT == "reddit"
    assert SourceType.YOUTUBE == "youtube"
