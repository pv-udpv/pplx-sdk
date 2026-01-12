"""Tests for data models."""

import pytest

from pplx_sdk.models import ChatCompletionMessage, ChatCompletionRole


def test_chat_completion_message_creation():
    """Test ChatCompletionMessage creation."""
    msg = ChatCompletionMessage(role=ChatCompletionRole.USER, content="Hello")
    assert msg.role == ChatCompletionRole.USER
    assert msg.content == "Hello"


def test_chat_completion_message_serialization():
    """Test ChatCompletionMessage serialization."""
    msg = ChatCompletionMessage(role=ChatCompletionRole.ASSISTANT, content="Hi there")
    data = msg.model_dump()
    assert data["role"] == "assistant"
    assert data["content"] == "Hi there"
