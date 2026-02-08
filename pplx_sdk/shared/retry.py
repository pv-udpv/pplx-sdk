"""Retry and backoff utilities."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

from pplx_sdk.core.exceptions import TransportError

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        initial_backoff_ms: Initial backoff delay in milliseconds
        max_backoff_ms: Maximum backoff delay in milliseconds
        backoff_multiplier: Multiplier for exponential backoff
        jitter: Whether to add random jitter to backoff
    """

    max_retries: int = 3
    initial_backoff_ms: int = 1000
    max_backoff_ms: int = 30000
    backoff_multiplier: float = 2.0
    jitter: bool = True

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff delay for given attempt.

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        backoff = min(
            self.initial_backoff_ms * (self.backoff_multiplier**attempt),
            self.max_backoff_ms,
        )

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = backoff * 0.25
            backoff += random.uniform(-jitter_range, jitter_range)  # noqa: S311

        return backoff / 1000.0  # Convert to seconds


def retry_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple[type[Exception], ...] = (TransportError,),
) -> T:
    """Retry function with exponential backoff.

    Args:
        func: Function to retry (takes no arguments)
        config: Retry configuration
        retryable_exceptions: Exceptions that trigger retry

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    config = config or RetryConfig()
    last_exception: Optional[Exception] = None

    for attempt in range(config.max_retries + 1):
        try:
            return func()
        except retryable_exceptions as exc:
            last_exception = exc

            if attempt == config.max_retries:
                raise

            delay = config.calculate_backoff(attempt)
            time.sleep(delay)

    # This should never be reached, but helps type checker
    assert last_exception is not None  # noqa: S101
    raise last_exception
