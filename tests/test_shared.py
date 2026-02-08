"""Tests for shared retry module."""

import time

import pytest

from pplx_sdk.core.exceptions import TransportError
from pplx_sdk.shared.retry import RetryConfig, retry_with_backoff


def test_retry_config_defaults() -> None:
    """Test RetryConfig has correct defaults."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.initial_backoff_ms == 1000
    assert config.max_backoff_ms == 30000
    assert config.backoff_multiplier == 2.0
    assert config.jitter is True


def test_retry_config_calculate_backoff() -> None:
    """Test backoff calculation without jitter."""
    config = RetryConfig(
        initial_backoff_ms=1000,
        backoff_multiplier=2.0,
        jitter=False,
    )

    # attempt 0: 1000ms = 1.0s
    assert config.calculate_backoff(0) == 1.0
    # attempt 1: 2000ms = 2.0s
    assert config.calculate_backoff(1) == 2.0
    # attempt 2: 4000ms = 4.0s
    assert config.calculate_backoff(2) == 4.0


def test_retry_config_max_backoff() -> None:
    """Test backoff is capped at max_backoff_ms."""
    config = RetryConfig(
        initial_backoff_ms=1000,
        backoff_multiplier=10.0,
        max_backoff_ms=5000,
        jitter=False,
    )

    # attempt 1: would be 10000ms but capped at 5000ms = 5.0s
    assert config.calculate_backoff(1) == 5.0


def test_retry_config_calculate_backoff_with_jitter() -> None:
    """Test backoff calculation with jitter stays in range."""
    config = RetryConfig(
        initial_backoff_ms=1000,
        backoff_multiplier=2.0,
        jitter=True,
    )

    # With jitter, result should be within ±25% of base
    for _ in range(20):
        result = config.calculate_backoff(0)
        assert 0.75 <= result <= 1.25  # 1000ms ±25%


def test_retry_with_backoff_succeeds_first_try() -> None:
    """Test retry returns immediately on success."""
    call_count = 0

    def func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = retry_with_backoff(func)
    assert result == "success"
    assert call_count == 1


def test_retry_with_backoff_retries_on_failure() -> None:
    """Test retry retries on TransportError then succeeds."""
    call_count = 0

    def func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise TransportError("temporary failure")
        return "success"

    config = RetryConfig(
        max_retries=3,
        initial_backoff_ms=10,  # Short for testing
        jitter=False,
    )
    result = retry_with_backoff(func, config=config)
    assert result == "success"
    assert call_count == 3


def test_retry_with_backoff_exhausted() -> None:
    """Test retry raises after exhausting attempts."""

    def func():
        raise TransportError("permanent failure")

    config = RetryConfig(
        max_retries=2,
        initial_backoff_ms=10,
        jitter=False,
    )

    with pytest.raises(TransportError, match="permanent failure"):
        retry_with_backoff(func, config=config)


def test_retry_with_backoff_non_retryable() -> None:
    """Test non-retryable exceptions are raised immediately."""
    call_count = 0

    def func():
        nonlocal call_count
        call_count += 1
        raise ValueError("not retryable")

    config = RetryConfig(max_retries=3, initial_backoff_ms=10)

    with pytest.raises(ValueError, match="not retryable"):
        retry_with_backoff(func, config=config)

    assert call_count == 1  # Only called once, no retries
