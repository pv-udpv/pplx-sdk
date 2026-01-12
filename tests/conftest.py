"""Test configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_auth_token() -> str:
    """Mock authentication token for testing.

    Returns:
        Test authentication token
    """
    return "test-auth-token-12345"


@pytest.fixture
def mock_context_uuid() -> str:
    """Mock context UUID for testing.

    Returns:
        Test context UUID
    """
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def mock_frontend_uuid() -> str:
    """Mock frontend UUID for testing.

    Returns:
        Test frontend UUID
    """
    return "550e8400-e29b-41d4-a716-446655440001"


@pytest.fixture
def mock_backend_uuid() -> str:
    """Mock backend UUID for testing.

    Returns:
        Test backend UUID
    """
    return "backend-550e8400-e29b-41d4-a716-446655440002"
