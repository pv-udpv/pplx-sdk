"""OpenAI-compatible Pydantic models.

Provides data models matching OpenAI's Chat Completion API format.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message in OpenAI format."""

    role: Literal["system", "user", "assistant", "function"] = Field(
        description="Message role"
    )
    content: str = Field(description="Message content")
    name: Optional[str] = Field(default=None, description="Optional name for the message")


class ChatCompletionRequest(BaseModel):
    """OpenAI chat completion request format.

    Compatible with OpenAI's /v1/chat/completions endpoint.
    """

    model: str = Field(description="Model to use (e.g., pplx-70b-chat, gpt-4-turbo)")
    messages: List[ChatMessage] = Field(description="List of chat messages")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=2048, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Whether to stream responses")
    top_p: Optional[float] = Field(default=1.0, description="Nucleus sampling parameter")
    n: Optional[int] = Field(default=1, description="Number of completions")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(
        default=0.0, description="Presence penalty"
    )
    frequency_penalty: Optional[float] = Field(
        default=0.0, description="Frequency penalty"
    )


class ChatCompletionChoice(BaseModel):
    """Chat completion choice."""

    index: int = Field(description="Choice index")
    message: ChatMessage = Field(description="Generated message")
    finish_reason: Optional[str] = Field(
        default=None, description="Reason for completion finish"
    )


class ChatCompletionUsage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = Field(description="Tokens in prompt")
    completion_tokens: int = Field(description="Tokens in completion")
    total_tokens: int = Field(description="Total tokens")


class ChatCompletionResponse(BaseModel):
    """OpenAI chat completion response format."""

    id: str = Field(description="Unique completion ID")
    object: Literal["chat.completion"] = Field(
        default="chat.completion", description="Object type"
    )
    created: int = Field(description="Unix timestamp")
    model: str = Field(description="Model used")
    choices: List[ChatCompletionChoice] = Field(description="Generated choices")
    usage: Optional[ChatCompletionUsage] = Field(
        default=None, description="Token usage stats"
    )


class ChatCompletionChunkDelta(BaseModel):
    """Delta content in streaming chunk."""

    role: Optional[str] = Field(default=None, description="Message role")
    content: Optional[str] = Field(default=None, description="Content delta")


class ChatCompletionChunkChoice(BaseModel):
    """Streaming chunk choice."""

    index: int = Field(description="Choice index")
    delta: ChatCompletionChunkDelta = Field(description="Content delta")
    finish_reason: Optional[str] = Field(
        default=None, description="Reason for completion finish"
    )


class ChatCompletionChunk(BaseModel):
    """OpenAI streaming chunk format."""

    id: str = Field(description="Unique completion ID")
    object: Literal["chat.completion.chunk"] = Field(
        default="chat.completion.chunk", description="Object type"
    )
    created: int = Field(description="Unix timestamp")
    model: str = Field(description="Model used")
    choices: List[ChatCompletionChunkChoice] = Field(description="Streaming choices")


class Model(BaseModel):
    """OpenAI model information."""

    id: str = Field(description="Model identifier")
    object: Literal["model"] = Field(default="model", description="Object type")
    created: int = Field(description="Unix timestamp")
    owned_by: str = Field(description="Organization owning the model")


class ModelList(BaseModel):
    """List of available models."""

    object: Literal["list"] = Field(default="list", description="Object type")
    data: List[Model] = Field(description="List of models")


# Model mapping from OpenAI to Perplexity
MODEL_MAPPING: Dict[str, Dict[str, Any]] = {
    "gpt-4-turbo": {
        "pplx_model": "pplx-70b-deep",
        "mode": "research",
        "description": "Research mode with deep analysis",
    },
    "gpt-4": {
        "pplx_model": "pplx-70b-chat",
        "mode": "concise",
        "description": "Standard mode with 70B model",
    },
    "gpt-3.5-turbo": {
        "pplx_model": "pplx-7b-online",
        "mode": "concise",
        "description": "Fast mode with smaller model",
    },
    "pplx-70b-chat": {
        "pplx_model": "pplx-70b-chat",
        "mode": "concise",
        "description": "Native Perplexity 70B chat",
    },
    "pplx-70b-deep": {
        "pplx_model": "pplx-70b-deep",
        "mode": "research",
        "description": "Native Perplexity deep research",
    },
    "pplx-7b-online": {
        "pplx_model": "pplx-7b-online",
        "mode": "concise",
        "description": "Native Perplexity fast mode",
    },
}
