"""Data models for Perplexity AI SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ChatCompletionRole(str, Enum):
    """Chat completion role."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatCompletionMessage(BaseModel):
    """Chat completion message."""

    role: ChatCompletionRole
    content: str
    name: Optional[str] = None


class Delta(BaseModel):
    """Delta for streaming responses."""

    role: Optional[ChatCompletionRole] = None
    content: Optional[str] = None


class CompletionUsage(BaseModel):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Chat(BaseModel):
    """Chat request payload."""

    model: str
    messages: list[ChatCompletionMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stream: bool = False

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ChatCompletion(BaseModel):
    """Chat completion response."""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[dict[str, Any]] = Field(default_factory=list)
    usage: CompletionUsage
    system_fingerprint: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Streaming chat completion chunk."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[dict[str, Any]] = Field(default_factory=list)
    system_fingerprint: Optional[str] = None
