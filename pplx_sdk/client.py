"""Main client and conversation API for Perplexity SDK.

Provides high-level interfaces for interacting with Perplexity API.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional

import httpx

from pplx_sdk.domain.articles import ArticlesService
from pplx_sdk.domain.collections import CollectionsService
from pplx_sdk.domain.entries import EntriesService
from pplx_sdk.domain.memories import MemoriesService
from pplx_sdk.domain.models import Entry, MessageChunk, Thread, ThreadAccess
from pplx_sdk.domain.threads import ThreadsService
from pplx_sdk.transport.http import HttpTransport
from pplx_sdk.transport.sse import SSETransport


class PerplexityClient:
    """Main client for Perplexity API.

    Provides access to all domain services and high-level conversation API.

    Example:
        >>> client = PerplexityClient(auth_token="session-token")
        >>> conv = client.new_conversation(title="Research")
        >>> entry = conv.ask("What is quantum computing?")
    """

    def __init__(
        self,
        api_base: str = "https://www.perplexity.ai",
        auth_token: Optional[str] = None,
        timeout: float = 30.0,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize Perplexity client.

        Args:
            api_base: Base URL for API requests
            auth_token: Authentication token (session ID from cookies)
            timeout: Request timeout in seconds
            default_headers: Additional headers for all requests
        """
        self.api_base = api_base
        self.auth_token = auth_token
        self.timeout = timeout
        self.default_headers = default_headers or {}

        # Create HTTP client
        self._http_client = httpx.Client(
            base_url=api_base,
            timeout=timeout,
            headers=self._build_headers(),
            follow_redirects=True,
        )

        # Initialize transport layers
        self._sse_transport = SSETransport(
            client=self._http_client,
            endpoint="/rest/sse/perplexity.ask",
        )

        # Initialize domain services
        self._threads_service = ThreadsService()
        self._entries_service = EntriesService(self._sse_transport)
        self._memories_service = MemoriesService()
        self._collections_service = CollectionsService()
        self._articles_service = ArticlesService()

    def _build_headers(self) -> Dict[str, str]:
        """Build default headers for requests.

        Returns:
            Dictionary of default headers
        """
        headers = {
            "User-Agent": "pplx-sdk/0.1.0",
            "X-Client-Name": "web",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        headers.update(self.default_headers)
        return headers

    @property
    def threads(self) -> ThreadsService:
        """Access threads service.

        Returns:
            ThreadsService instance
        """
        return self._threads_service

    @property
    def entries(self) -> EntriesService:
        """Access entries service.

        Returns:
            EntriesService instance
        """
        return self._entries_service

    @property
    def memories(self) -> MemoriesService:
        """Access memories service.

        Returns:
            MemoriesService instance
        """
        return self._memories_service

    @property
    def collections(self) -> CollectionsService:
        """Access collections service.

        Returns:
            CollectionsService instance
        """
        return self._collections_service

    @property
    def articles(self) -> ArticlesService:
        """Access articles service.

        Returns:
            ArticlesService instance
        """
        return self._articles_service

    def new_conversation(self, title: Optional[str] = None) -> "Conversation":
        """Create a new conversation.

        Args:
            title: Optional conversation title

        Returns:
            Conversation instance
        """
        # Generate new context UUID
        context_uuid = str(uuid.uuid4())

        # Create thread object
        thread = Thread(
            context_uuid=context_uuid,
            title=title,
            slug=f"conv-{context_uuid[:8]}",
            access=ThreadAccess.PRIVATE,
        )

        return Conversation(client=self, thread=thread, entries=[])

    def conversation_from_thread(self, slug_or_uuid: str) -> "Conversation":
        """Load an existing conversation from a thread.

        Args:
            slug_or_uuid: Thread slug or UUID

        Returns:
            Conversation instance

        Raises:
            ValueError: If thread not found
        """
        # Try to get thread
        thread = self._threads_service.get(slug_or_uuid)

        if not thread:
            raise ValueError(f"Thread not found: {slug_or_uuid}")

        return Conversation(client=self, thread=thread, entries=[])

    def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._http_client:
            self._http_client.close()

    def __enter__(self) -> "PerplexityClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


@dataclass
class Conversation:
    """Stateful conversation wrapper.

    Manages a conversation thread with automatic parent tracking.

    Example:
        >>> conv = client.new_conversation(title="Research")
        >>> for chunk in conv.ask_stream("What is AI?"):
        ...     print(chunk.text, end="")
        >>> entry = conv.ask("Tell me more")
        >>> forked = conv.fork(from_entry=entry)
    """

    client: PerplexityClient
    thread: Thread
    entries: List[Entry] = field(default_factory=list)

    @property
    def context_uuid(self) -> str:
        """Get conversation context UUID.

        Returns:
            Context UUID string
        """
        return self.thread.context_uuid

    def ask_stream(
        self,
        query: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Generator[MessageChunk, None, None]:
        """Ask a question and stream the response.

        Args:
            query: Question to ask
            mode: Query mode (concise, research, etc.)
            model_preference: Model to use
            sources: List of source types
            **kwargs: Additional parameters

        Yields:
            MessageChunk objects from SSE stream
        """
        # Get parent entry UUID if we have entries
        parent_entry_uuid = None
        if self.entries:
            parent_entry_uuid = self.entries[-1].backend_uuid

        # Stream from entries service
        yield from self.client.entries.stream_ask(
            query=query,
            context_uuid=self.context_uuid,
            mode=mode,
            model_preference=model_preference,
            sources=sources,
            parent_entry_uuid=parent_entry_uuid,
            **kwargs,
        )

    def ask(
        self,
        query: str,
        mode: str = "concise",
        model_preference: str = "pplx-70b-chat",
        sources: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Entry:
        """Ask a question and return the complete entry.

        The entry is automatically added to the conversation history.

        Args:
            query: Question to ask
            mode: Query mode
            model_preference: Model to use
            sources: List of source types
            **kwargs: Additional parameters

        Returns:
            Complete Entry object
        """
        # Get parent entry UUID if we have entries
        parent_entry_uuid = None
        if self.entries:
            parent_entry_uuid = self.entries[-1].backend_uuid

        # Get full entry
        entry = self.client.entries.ask(
            query=query,
            context_uuid=self.context_uuid,
            mode=mode,
            model_preference=model_preference,
            sources=sources,
            parent_entry_uuid=parent_entry_uuid,
            **kwargs,
        )

        # Add to conversation history
        self.entries.append(entry)

        return entry

    def fork(self, from_entry: Optional[Entry] = None) -> "Conversation":
        """Fork the conversation at a specific entry.

        Creates a new conversation with entries up to the fork point.

        Args:
            from_entry: Entry to fork from (default: last entry)

        Returns:
            New Conversation instance
        """
        # Determine fork point
        if from_entry is None:
            fork_entries = self.entries.copy()
        else:
            # Find entry index
            try:
                fork_idx = self.entries.index(from_entry)
                fork_entries = self.entries[: fork_idx + 1]
            except ValueError:
                fork_entries = []

        # Create new thread
        new_context_uuid = str(uuid.uuid4())
        new_thread = Thread(
            context_uuid=new_context_uuid,
            title=f"{self.thread.title} (fork)" if self.thread.title else "Forked conversation",
            slug=f"fork-{new_context_uuid[:8]}",
            access=self.thread.access,
        )

        return Conversation(client=self.client, thread=new_thread, entries=fork_entries)

    def save_to_collection(self, collection_id: str) -> None:
        """Save conversation to a collection.

        Args:
            collection_id: Target collection ID
        """
        self.client.collections.save_thread(self.context_uuid, collection_id)

    def to_article(self) -> Optional[dict]:
        """Convert conversation to an article.

        Returns:
            Article data if successful, None otherwise
        """
        return self.client.articles.from_thread(self.context_uuid)
