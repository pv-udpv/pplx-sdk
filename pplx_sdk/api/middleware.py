from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("pplx_sdk.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log details.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response object

        """
        # Log request
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status {response.status_code} - Duration {duration:.3f}s"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} - "
                f"Duration {duration:.3f}s - Error: {e!s}"
            )
            raise


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication (placeholder).

    Note: Currently auth is handled via PPLX_AUTH_TOKEN env var.
    This middleware can be extended for request-level auth.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with auth checks.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response object

        """
        # TODO: Add request-level auth if needed
        # For now, just pass through
        return await call_next(request)
